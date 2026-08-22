#!/usr/bin/env python3
"""Validate or execute a preregistered provider-neutral evaluation matrix."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.experiment_core import (
    ExperimentDataError,
    audit_result_file,
    canonical_json_hash,
    execution_jobs,
    file_sha256,
    job_relative_output,
    load_experiment,
    validate_experiment,
)

ROOT = Path(__file__).resolve().parents[1]


def _resolve(config_path: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = config_path.parent / path
    return path.resolve()


def _adapter_command(command: list[str]) -> list[str]:
    return [sys.executable if part == "${PYTHON}" else part for part in command]


def _run_job(
    manifest: dict[str, Any],
    runner_config: dict[str, Any],
    config_path: Path,
    job: dict[str, Any],
    output_root: Path,
    *,
    resume: bool,
    retry_reason: str | None,
) -> dict[str, Any]:
    relative_output = job_relative_output(job)
    output_path = output_root / relative_output
    if output_path.exists():
        if not resume:
            raise ExperimentDataError(f"output already exists: {relative_output}")
        errors = audit_result_file(manifest, job, output_path)
        if errors:
            raise ExperimentDataError(
                f"cannot resume invalid output {relative_output}: {'; '.join(errors)}"
            )
        return {
            "output": relative_output.as_posix(),
            "sha256": file_sha256(output_path),
            "status": "reused",
            "execution_attempt": job["execution_attempt"],
            "retry_reason": retry_reason,
        }

    limits = runner_config["limits"]
    baseline = _resolve(config_path, runner_config["baseline_skill_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output_path.with_name(f".{output_path.name}.{uuid.uuid4().hex}.tmp")
    with tempfile.TemporaryDirectory(prefix="intent-naming-study-") as temporary_directory:
        temporary = Path(temporary_directory)
        implementation_path = temporary / "implementation.json"
        implementation_path.write_text(
            json.dumps(job["implementation"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        command = [
            sys.executable,
            str(ROOT / "harness" / "run_adapter.py"),
            "--cases",
            str(job["cases_path"]),
            "--output",
            str(temporary_output),
            "--variant",
            job["variant"],
            "--system-id",
            job["system_id"],
            "--replicate-id",
            job["replicate_id"],
            "--run-id",
            manifest["experiment_id"],
            "--implementation-json",
            str(implementation_path),
            "--attempt",
            str(job["execution_attempt"]),
            "--timeout-seconds",
            str(limits["timeout_seconds"]),
            "--max-input-bytes",
            str(limits["max_input_bytes"]),
            "--max-output-bytes",
            str(limits["max_output_bytes"]),
            "--max-stderr-bytes",
            str(limits["max_stderr_bytes"]),
        ]
        if job["variant"] == "previous-skill":
            command.extend(["--baseline-skill-path", str(baseline)])
        command.extend(["--", *_adapter_command(job["adapter_command"])])
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                env=os.environ.copy(),
            )
            if completed.returncode != 0:
                raise ExperimentDataError(
                    f"job {relative_output} failed with {completed.returncode}; "
                    "adapter stderr was withheld from the evidence ledger"
                )
            errors = audit_result_file(manifest, job, temporary_output)
            if errors:
                raise ExperimentDataError(
                    f"job {relative_output} produced invalid evidence: {'; '.join(errors)}"
                )
            temporary_output.replace(output_path)
        finally:
            temporary_output.unlink(missing_ok=True)
    return {
        "output": relative_output.as_posix(),
        "sha256": file_sha256(output_path),
        "status": "completed",
        "execution_attempt": job["execution_attempt"],
        "retry_reason": retry_reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runner-config", type=Path, required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="run paid/external adapters; without this flag only validate and print the matrix",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--retry-reason",
        choices=("transport-error", "provider-timeout", "provider-unavailable"),
        help="required when retrying a previously failed job",
    )
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    config_path = args.runner_config.resolve()
    try:
        manifest, runner_config = load_experiment(manifest_path, config_path)
        validation = validate_experiment(
            manifest,
            runner_config,
            runner_config_path=config_path,
        )
        if validation["errors"]:
            raise ExperimentDataError("; ".join(validation["errors"]))
        jobs = execution_jobs(manifest, validation)
    except ExperimentDataError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    summary = {
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": validation["manifest_sha256"],
        "datasets": len(manifest["datasets"]),
        "systems": len(manifest["systems"]),
        "variants": len(manifest["variants"]),
        "replicates": len(manifest["replicate_ids"]),
        "jobs": len(jobs),
        "mode": "execute" if args.execute else "validate-only",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not args.execute:
        return 0

    output_root = _resolve(config_path, runner_config["output_root"])
    if output_root == ROOT or output_root == ROOT.parent:
        print("output_root cannot be the repository or workspace root", file=sys.stderr)
        return 2
    experiment_root = output_root / manifest["experiment_id"]
    existing_outputs = [
        job_relative_output(job)
        for job in jobs
        if (experiment_root / job_relative_output(job)).exists()
    ]
    if existing_outputs and not args.resume:
        print(
            f"{len(existing_outputs)} result files already exist; use --resume after verifying them",
            file=sys.stderr,
        )
        return 2
    experiment_root.mkdir(parents=True, exist_ok=True)
    ledger_path = experiment_root / "evidence-ledger.json"
    previous_ledger: dict[str, Any] = {}
    if args.resume and ledger_path.exists():
        try:
            previous_ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"cannot resume invalid evidence ledger: {exc}", file=sys.stderr)
            return 2
        if previous_ledger.get("manifest_sha256") != validation["manifest_sha256"]:
            print("cannot resume a ledger from a different manifest", file=sys.stderr)
            return 2
    previous_records = [
        record
        for record in previous_ledger.get("jobs", [])
        if isinstance(record, dict) and isinstance(record.get("output"), str)
    ]
    attempts_by_output: dict[str, int] = {}
    failed_outputs: set[str] = set()
    for record in previous_records:
        relative = record["output"]
        attempt = record.get("execution_attempt", 1)
        if isinstance(attempt, int) and not isinstance(attempt, bool):
            attempts_by_output[relative] = max(attempts_by_output.get(relative, 0), attempt)
        if record.get("status") == "failed":
            failed_outputs.add(relative)
        elif record.get("status") in {"completed", "reused"}:
            failed_outputs.discard(relative)
    if failed_outputs and args.resume and not args.retry_reason:
        print("--retry-reason is required to resume previously failed jobs", file=sys.stderr)
        return 2
    allowed_retry_reasons = set(manifest["analysis"]["retry_policy"]["allowed_reasons"])
    if args.retry_reason and args.retry_reason not in allowed_retry_reasons:
        print("--retry-reason is not allowed by the frozen manifest", file=sys.stderr)
        return 2
    maximum_attempts = manifest["analysis"]["retry_policy"]["maximum_attempts"]
    scheduled_jobs: list[dict[str, Any]] = []
    for job in jobs:
        relative = job_relative_output(job).as_posix()
        path = experiment_root / Path(relative)
        previous_attempt = attempts_by_output.get(relative, 0)
        execution_attempt = max(previous_attempt, 1) if path.exists() else previous_attempt + 1
        if not path.exists() and execution_attempt > maximum_attempts:
            print(f"retry limit reached for {relative}", file=sys.stderr)
            return 2
        scheduled_jobs.append({**job, "execution_attempt": execution_attempt})
    started_at = datetime.now(UTC).isoformat()
    records: list[dict[str, Any]] = list(previous_records)
    current_failures: list[str] = []
    with ThreadPoolExecutor(max_workers=runner_config["limits"]["max_workers"]) as executor:
        pending = {
            executor.submit(
                _run_job,
                manifest,
                runner_config,
                config_path,
                job,
                experiment_root,
                resume=args.resume,
                retry_reason=(
                    args.retry_reason
                    if job_relative_output(job).as_posix() in failed_outputs
                    else None
                ),
            ): job
            for job in scheduled_jobs
        }
        for future in as_completed(pending):
            job = pending[future]
            try:
                records.append(future.result())
            except ExperimentDataError as exc:
                message = str(exc)
                current_failures.append(message)
                records.append(
                    {
                        "output": job_relative_output(job).as_posix(),
                        "sha256": None,
                        "status": "failed",
                        "execution_attempt": job["execution_attempt"],
                        "retry_reason": (
                            args.retry_reason
                            if job_relative_output(job).as_posix() in failed_outputs
                            else None
                        ),
                    }
                )
                print(message, file=sys.stderr)
    all_outputs_exist = all((experiment_root / job_relative_output(job)).is_file() for job in jobs)
    ledger = {
        "schema_version": "1.0",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": validation["manifest_sha256"],
        "runner_config_sha256": canonical_json_hash(runner_config),
        "started_at": started_at,
        "finished_at": datetime.now(UTC).isoformat(),
        "complete": not current_failures and all_outputs_exist,
        "jobs": sorted(
            records,
            key=lambda item: (item["output"], item.get("execution_attempt", 1)),
        ),
        "failures": [
            *previous_ledger.get("failures", []),
            *current_failures,
        ],
    }
    temporary_ledger = experiment_root / ".evidence-ledger.json.tmp"
    temporary_ledger.write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary_ledger.replace(ledger_path)
    print(f"ledger: {ledger_path}")
    return 0 if ledger["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
