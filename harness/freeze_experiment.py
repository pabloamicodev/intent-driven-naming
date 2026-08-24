#!/usr/bin/env python3
"""Freeze dataset, runtime, and policy identities into an experiment manifest."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.eval_core import EvaluationDataError, load_case_map
from harness.experiment_core import (
    ExperimentDataError,
    canonical_json_hash,
    file_sha256,
    load_experiment,
    runtime_sha256,
    validate_experiment,
)


def _resolve(config_path: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = config_path.parent / path
    return path.resolve()


def freeze_manifest(
    draft: dict[str, Any],
    runner_config: dict[str, Any],
    *,
    runner_config_path: Path,
) -> dict[str, Any]:
    manifest = copy.deepcopy(draft)
    manifest.setdefault("schema_version", "1.0")
    manifest.setdefault("created_at", datetime.now(UTC).isoformat())
    configured_datasets = {item["dataset_id"]: item for item in runner_config.get("datasets", [])}
    versions: set[str] = set()
    for dataset in manifest.get("datasets", []):
        dataset_id = dataset.get("dataset_id")
        configured = configured_datasets.get(dataset_id)
        if configured is None:
            raise ExperimentDataError(f"runner configuration is missing dataset {dataset_id}")
        for part in ("activation", "behavior"):
            path = _resolve(runner_config_path, configured[f"{part}_cases"])
            try:
                cases = load_case_map([path])
            except EvaluationDataError as exc:
                raise ExperimentDataError(str(exc)) from exc
            versions.update(case["dataset_version"] for case in cases.values())
            dataset[part] = {"sha256": file_sha256(path), "records": len(cases)}
    if len(versions) != 1:
        raise ExperimentDataError(f"experiment datasets have mixed versions: {sorted(versions)}")
    manifest["dataset_version"] = next(iter(versions))

    policy_path = _resolve(runner_config_path, runner_config["release_policy_path"])
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentDataError(f"cannot load release policy: {exc}") from exc
    manifest["release_policy"] = {
        "version": policy["version"],
        "sha256": file_sha256(policy_path),
    }
    manifest["skills"] = {}
    for label, config_field in (
        ("with_skill", "current_skill_path"),
        ("previous_skill", "baseline_skill_path"),
    ):
        path = _resolve(runner_config_path, runner_config[config_field])
        try:
            version = (path / "VERSION").read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ExperimentDataError(f"cannot load {label} VERSION: {exc}") from exc
        manifest["skills"][label] = {
            "version": version,
            "sha256": runtime_sha256(path),
        }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--runner-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    draft_path = args.draft.resolve()
    config_path = args.runner_config.resolve()
    output_path = args.output.resolve()
    if output_path.exists() and not args.replace:
        print("output exists; pass --replace to replace it", file=sys.stderr)
        return 2
    try:
        draft, runner_config = load_experiment(draft_path, config_path)
        manifest = freeze_manifest(
            draft,
            runner_config,
            runner_config_path=config_path,
        )
        validation = validate_experiment(
            manifest,
            runner_config,
            runner_config_path=config_path,
        )
        if validation["errors"]:
            raise ExperimentDataError("; ".join(validation["errors"]))
    except (ExperimentDataError, AttributeError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(f".{output_path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(output_path)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"manifest_sha256: {canonical_json_hash(manifest)}")
    print(f"manifest: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
