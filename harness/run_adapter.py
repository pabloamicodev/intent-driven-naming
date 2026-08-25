#!/usr/bin/env python3
"""Run a provider-neutral JSONL adapter against evaluation cases."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.eval_core import (
    EvaluationDataError,
    canonical_configuration_hash,
    load_case_map,
    validate_result,
    write_jsonl,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True, help="JSONL case dataset")
    parser.add_argument("--output", type=Path, required=True, help="raw result JSONL")
    parser.add_argument(
        "--variant",
        choices=("with-skill", "previous-skill", "without-skill"),
        required=True,
    )
    parser.add_argument(
        "--baseline-skill-path",
        type=Path,
        help="required frozen runtime checkout for the previous-skill variant",
    )
    parser.add_argument(
        "--system-id", required=True, help="stable model-and-agent configuration name"
    )
    parser.add_argument("--replicate-id", default="r1")
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument(
        "--implementation-json",
        type=Path,
        help="optional pinned implementation metadata; otherwise the adapter must return it",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--max-input-bytes", type=int, default=10_000_000)
    parser.add_argument("--max-output-bytes", type=int, default=10_000_000)
    parser.add_argument("--max-stderr-bytes", type=int, default=1_000_000)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("adapter", nargs=argparse.REMAINDER, help="adapter command after --")
    args = parser.parse_args()

    adapter = args.adapter
    if adapter and adapter[0] == "--":
        adapter = adapter[1:]
    if not adapter:
        parser.error("an adapter command is required after --")
    if args.timeout_seconds < 1:
        parser.error("--timeout-seconds must be at least 1")
    if min(args.max_input_bytes, args.max_output_bytes, args.max_stderr_bytes) < 1:
        parser.error("adapter byte limits must be at least 1")
    if args.limit is not None and args.limit < 0:
        parser.error("--limit cannot be negative")
    if args.attempt < 1:
        parser.error("--attempt must be at least 1")
    if args.variant == "previous-skill" and not args.baseline_skill_path:
        parser.error("--baseline-skill-path is required for previous-skill")
    if args.baseline_skill_path and not (args.baseline_skill_path / "SKILL.md").is_file():
        parser.error("--baseline-skill-path must contain SKILL.md")
    if not args.replicate_id.strip() or not args.system_id.strip():
        parser.error("--system-id and --replicate-id must be non-empty")

    declared_implementation = None
    if args.implementation_json:
        try:
            declared_implementation = json.loads(
                args.implementation_json.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"cannot read --implementation-json: {exc}")
        if not isinstance(declared_implementation, dict):
            parser.error("--implementation-json must contain a JSON object")

    try:
        case_map = load_case_map([args.cases])
    except EvaluationDataError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    cases = list(case_map.values())
    if args.limit is not None:
        cases = cases[: args.limit]
    run_id = args.run_id or f"run-{uuid.uuid4().hex[:12]}"
    requests = []
    for case in cases:
        requests.append(
            {
                "protocol_version": 1,
                "run_id": run_id,
                "system_id": args.system_id,
                "replicate_id": args.replicate_id,
                "attempt": args.attempt,
                "declared_implementation": declared_implementation,
                "case": case,
                "skill_path": str(
                    args.baseline_skill_path.resolve()
                    if args.variant == "previous-skill"
                    else (ROOT / "skills" / "intent-driven-naming").resolve()
                ),
                "variant": args.variant,
            }
        )
    payload = "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in requests)
    payload_bytes = payload.encode("utf-8")
    if len(payload_bytes) > args.max_input_bytes:
        print(
            f"adapter input exceeded --max-input-bytes: "
            f"{len(payload_bytes)} > {args.max_input_bytes}",
            file=sys.stderr,
        )
        return 2

    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        try:
            completed = subprocess.run(
                adapter,
                input=payload_bytes,
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=args.timeout_seconds,
                cwd=ROOT,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"adapter execution failed: {exc}", file=sys.stderr)
            return 2
        stdout_size = stdout_file.tell()
        stderr_size = stderr_file.tell()
        if stderr_size > args.max_stderr_bytes:
            print(
                f"adapter stderr exceeded --max-stderr-bytes: "
                f"{stderr_size} > {args.max_stderr_bytes}",
                file=sys.stderr,
            )
            return 2
        stderr_file.seek(0)
        stderr_text = stderr_file.read().decode("utf-8", errors="replace")
        if stderr_text:
            print(stderr_text, file=sys.stderr, end="")
        if completed.returncode != 0:
            print(f"adapter exited with {completed.returncode}", file=sys.stderr)
            return completed.returncode
        if stdout_size > args.max_output_bytes:
            print(
                f"adapter stdout exceeded --max-output-bytes: "
                f"{stdout_size} > {args.max_output_bytes}",
                file=sys.stderr,
            )
            return 2
        stdout_file.seek(0)
        try:
            stdout = stdout_file.read().decode("utf-8")
        except UnicodeDecodeError as exc:
            print(f"adapter stdout is not UTF-8: {exc}", file=sys.stderr)
            return 2

    responses = []
    for line_number, line in enumerate(stdout.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            response = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"adapter stdout line {line_number} is not JSON: {exc}", file=sys.stderr)
            return 2
        if not isinstance(response, dict):
            print(f"adapter stdout line {line_number} must be a JSON object", file=sys.stderr)
            return 2
        responses.append(response)
    response_ids = [response.get("case_id") for response in responses]
    expected_ids = [case["id"] for case in cases]
    if response_ids != expected_ids:
        print(
            f"adapter response IDs do not match request order: expected {expected_ids}, got {response_ids}",
            file=sys.stderr,
        )
        return 2
    for response in responses:
        case = case_map[response["case_id"]]
        protected_fields = (
            ("run_id", run_id),
            ("system_id", args.system_id),
            ("replicate_id", args.replicate_id),
            ("attempt", args.attempt),
            ("dataset_version", case["dataset_version"]),
            ("variant", args.variant),
        )
        for field, expected in protected_fields:
            if field in response and response[field] != expected:
                print(
                    f"adapter response {response['case_id']} attempted to change {field}",
                    file=sys.stderr,
                )
                return 2
        response.setdefault("schema_version", "1.0")
        response.setdefault("protocol_version", 1)
        response.setdefault("run_id", run_id)
        response.setdefault("system_id", args.system_id)
        response.setdefault("replicate_id", args.replicate_id)
        response.setdefault("attempt", args.attempt)
        response.setdefault("dataset_version", case["dataset_version"])
        response.setdefault("variant", args.variant)
        if declared_implementation is not None:
            if (
                "implementation" in response
                and response["implementation"] != declared_implementation
            ):
                print(
                    f"adapter response {response['case_id']} implementation metadata differs from the declared configuration",
                    file=sys.stderr,
                )
                return 2
            response["implementation"] = declared_implementation
        implementation = response.get("implementation")
        if not isinstance(implementation, dict) or not implementation:
            print(
                f"adapter response {response['case_id']} requires implementation metadata",
                file=sys.stderr,
            )
            return 2
        response["configuration_hash"] = canonical_configuration_hash(implementation)
        validation_errors = validate_result(response, case_map)
        if validation_errors:
            print(
                f"adapter response {response['case_id']} is invalid: {'; '.join(validation_errors)}",
                file=sys.stderr,
            )
            return 2
        if (
            response["status"] == "completed"
            and case["suite"] == "activation"
            and not isinstance(response.get("selected_skill"), bool)
        ):
            print(
                f"adapter response {response['case_id']} requires selected_skill",
                file=sys.stderr,
            )
            return 2
        if response["status"] == "completed" and case["suite"] == "behavior":
            output_text = response.get("output_text")
            bundle = response.get("artifact_bundle")
            if (not isinstance(output_text, str) or not output_text.strip()) and not bundle:
                print(
                    f"adapter response {response['case_id']} requires output_text or artifact_bundle",
                    file=sys.stderr,
                )
                return 2
    write_jsonl(args.output, responses)
    print(f"wrote {len(responses)} results to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
