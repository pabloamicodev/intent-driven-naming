#!/usr/bin/env python3
"""Validate private evaluation JSONL and print a prompt-free integrity summary."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.eval_core import EvaluationDataError, read_jsonl, validate_case

ROOT = Path(__file__).resolve().parents[1]


def validate_private_suite(paths: list[Path]) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    public_ids: set[str] = set()
    for public_path in sorted((ROOT / "evals" / "cases").glob("*.jsonl")):
        public_ids.update(record["id"] for record in read_jsonl(public_path))
    cases: list[dict[str, object]] = []
    digests: dict[str, str] = {}
    for path in paths:
        try:
            records = read_jsonl(path)
        except (OSError, EvaluationDataError) as exc:
            errors.append(str(exc))
            continue
        cases.extend(records)
        digests[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    ids = [str(case.get("id")) for case in cases]
    duplicates = sorted(case_id for case_id, count in Counter(ids).items() if count > 1)
    overlap = sorted(set(ids) & public_ids)
    if duplicates:
        errors.append(f"duplicate private IDs: {duplicates}")
    if overlap:
        errors.append(f"private IDs overlap public cases: {overlap}")
    versions = {case.get("dataset_version") for case in cases}
    if len(versions) > 1:
        errors.append("private files use multiple dataset versions")
    for case in cases:
        errors.extend(f"{case.get('id', '?')}: {error}" for error in validate_case(case))
    summary: dict[str, object] = {
        "schema_version": "1.0",
        "valid": not errors,
        "case_count": len(cases),
        "suite_counts": dict(sorted(Counter(str(case.get("suite")) for case in cases).items())),
        "locale_counts": dict(sorted(Counter(str(case.get("locale")) for case in cases).items())),
        "difficulty_counts": dict(
            sorted(Counter(str(case.get("difficulty")) for case in cases).items())
        ),
        "dataset_versions": sorted(str(version) for version in versions),
        "file_sha256": dict(sorted(digests.items())),
        "errors": errors,
    }
    return errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=Path, nargs="+")
    args = parser.parse_args()
    errors, summary = validate_private_suite([path.resolve() for path in args.paths])
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
