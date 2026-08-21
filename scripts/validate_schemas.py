#!/usr/bin/env python3
"""Validate JSON Schemas and checked-in data with the pinned development validator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError, ValidationError
    except ImportError:
        print("install requirements-dev.txt before running schema validation", file=sys.stderr)
        return 2

    schema_dir = ROOT / "specification"
    schemas = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(schema_dir.glob("*.schema.json"))
    }
    try:
        for schema in schemas.values():
            Draft202012Validator.check_schema(schema)
        case_validator = Draft202012Validator(schemas["eval-case.schema.json"])
        case_count = 0
        for dataset in ("activation.jsonl", "behavior.jsonl"):
            for line in (ROOT / "evals" / "cases" / dataset).read_text(
                encoding="utf-8"
            ).splitlines():
                if line.strip():
                    case_validator.validate(json.loads(line))
                    case_count += 1
        Draft202012Validator(schemas["eval-manifest.schema.json"]).validate(
            json.loads((ROOT / "evals" / "manifest.json").read_text(encoding="utf-8"))
        )
        Draft202012Validator(schemas["fixture-manifest.schema.json"]).validate(
            json.loads((ROOT / "evals" / "fixtures" / "manifest.json").read_text(encoding="utf-8"))
        )
        Draft202012Validator(schemas["release-policy.schema.json"]).validate(
            json.loads((schema_dir / "release-policy.json").read_text(encoding="utf-8"))
        )
    except (KeyError, OSError, json.JSONDecodeError, SchemaError, ValidationError) as exc:
        message = f"schema validation failed: {exc}"
        if args.json_output:
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(
                json.dumps({"schema_version": "1.0", "valid": False, "error": message}, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        print(message, file=sys.stderr)
        return 1
    report = {
        "schema_version": "1.0",
        "valid": True,
        "schemas": len(schemas),
        "cases": case_count,
        "dataset_version": json.loads(
            (ROOT / "evals" / "manifest.json").read_text(encoding="utf-8")
        )["dataset_version"],
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(f"schema validation passed: schemas={len(schemas)} cases={case_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
