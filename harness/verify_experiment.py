#!/usr/bin/env python3
"""Verify every result and digest in an external experiment evidence ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.experiment_core import (
    ExperimentDataError,
    audit_result_file,
    execution_jobs,
    file_sha256,
    job_relative_output,
    load_experiment,
    validate_experiment,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runner-config", type=Path, required=True)
    parser.add_argument("--experiment-root", type=Path, required=True)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    config_path = args.runner_config.resolve()
    experiment_root = args.experiment_root.resolve()
    errors: list[str] = []
    try:
        manifest, runner_config = load_experiment(manifest_path, config_path)
        validation = validate_experiment(
            manifest,
            runner_config,
            runner_config_path=config_path,
        )
        errors.extend(validation["errors"])
        jobs = execution_jobs(manifest, validation) if not errors else []
    except ExperimentDataError as exc:
        errors.append(str(exc))
        manifest = {}
        validation = {"manifest_sha256": None}
        jobs = []

    ledger_path = experiment_root / "evidence-ledger.json"
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load evidence ledger: {exc}")
        ledger = {}
    if ledger.get("manifest_sha256") != validation.get("manifest_sha256"):
        errors.append("ledger manifest hash mismatch")
    ledger_jobs = {
        output: item
        for item in ledger.get("jobs", [])
        if isinstance(item, dict) and isinstance(output := item.get("output"), str)
    }
    for job in jobs:
        relative = job_relative_output(job).as_posix()
        path = experiment_root / Path(relative)
        if not path.is_file():
            errors.append(f"missing result file: {relative}")
            continue
        entry = ledger_jobs.get(relative)
        if not entry:
            errors.append(f"missing ledger entry: {relative}")
        elif entry.get("status") not in {"completed", "reused"}:
            errors.append(f"latest ledger entry is not successful: {relative}")
        elif entry.get("sha256") != file_sha256(path):
            errors.append(f"result hash mismatch: {relative}")
        errors.extend(f"{relative}: {error}" for error in audit_result_file(manifest, job, path))
    expected_outputs = {job_relative_output(job).as_posix() for job in jobs}
    extra_outputs = sorted(set(ledger_jobs) - expected_outputs)
    errors.extend(f"unexpected ledger output: {relative}" for relative in extra_outputs)
    if ledger.get("complete") is not True:
        errors.append("evidence ledger is not complete")
    report = {
        "schema_version": "1.0",
        "experiment_id": manifest.get("experiment_id"),
        "dataset_version": manifest.get("dataset_version"),
        "manifest_sha256": validation.get("manifest_sha256"),
        "purpose": manifest.get("purpose"),
        "claim_scope": manifest.get("claim_scope"),
        "held_out_dataset_present": any(
            dataset.get("visibility") == "held-out"
            for dataset in manifest.get("datasets", [])
            if isinstance(dataset, dict)
        ),
        "systems": len(manifest.get("systems", [])),
        "replicates": len(manifest.get("replicate_ids", [])),
        "expected_jobs": len(jobs),
        "verified_jobs": len(jobs)
        - sum(error.startswith("missing result file") for error in errors),
        "valid": not errors,
        "errors": errors,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
