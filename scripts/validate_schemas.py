#!/usr/bin/env python3
"""Validate JSON Schemas and checked-in data with the pinned development validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    try:
        from jsonschema import Draft202012Validator, FormatChecker
        from jsonschema.exceptions import SchemaError, ValidationError
        from referencing import Registry, Resource
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
        registry = Registry().with_resources(
            (schema["$id"], Resource.from_contents(schema))
            for schema in schemas.values()
            if "$id" in schema
        )
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
        Draft202012Validator(schemas["corpus-policy.schema.json"]).validate(
            json.loads((schema_dir / "corpus-policy.json").read_text(encoding="utf-8"))
        )
        experiment_manifest = json.loads(
            (ROOT / "examples" / "experiment-manifest.json").read_text(encoding="utf-8")
        )
        runner_config = json.loads(
            (ROOT / "examples" / "runner-config.json").read_text(encoding="utf-8")
        )
        Draft202012Validator(
            schemas["experiment-manifest.schema.json"],
            format_checker=FormatChecker(),
        ).validate(experiment_manifest)
        Draft202012Validator(schemas["runner-config.schema.json"]).validate(runner_config)
        rename_validator = Draft202012Validator(
            schemas["rename-plan.schema.json"], registry=registry
        )
        rename_example = json.loads(
            (ROOT / "examples" / "rename-plan.json").read_text(encoding="utf-8")
        )
        rename_validator.validate(rename_example)
        invalid_plans: list[tuple[str, dict]] = []
        low_materiality = copy.deepcopy(rename_example)
        low_materiality["records"][0]["materiality"] = "low"
        invalid_plans.append(("low-materiality change", low_materiality))
        low_confidence = copy.deepcopy(rename_example)
        low_confidence["records"][0]["confidence"] = "low"
        invalid_plans.append(("low-confidence change", low_confidence))
        incomplete_coverage = copy.deepcopy(rename_example)
        incomplete_coverage["records"][0]["decision"] = "map"
        incomplete_coverage["records"][0]["contract_risk"] = "external"
        incomplete_coverage["records"][0]["protected_spellings"] = ["result"]
        incomplete_coverage["analysis"]["reference_coverage"] = "partial"
        invalid_plans.append(("incomplete external coverage", incomplete_coverage))
        for label, invalid_plan in invalid_plans:
            if rename_validator.is_valid(invalid_plan):
                raise ValidationError(f"rename-plan schema accepted {label}")
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
