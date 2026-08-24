"""Preregistered experiment validation, execution planning, and evidence auditing."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, TypeGuard

from harness.create_artifact_bundle import SENSITIVE_CONTENT
from harness.eval_core import (
    BOOTSTRAP_SEED,
    VALID_VARIANTS,
    EvaluationDataError,
    canonical_configuration_hash,
    load_case_map,
    read_jsonl,
    validate_result,
)
from scripts.install_local_skill import runtime_files


class ExperimentDataError(ValueError):
    """Raised when a preregistered experiment or its evidence is inconsistent."""


SAFE_EXPERIMENT_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{5,79}$")
SAFE_LOCAL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def canonical_json_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_sha256(root: Path) -> str:
    files = runtime_files(root)
    if not files:
        raise ExperimentDataError(f"runtime has no files: {root}")
    inventory = {relative: file_sha256(path) for relative, path in sorted(files.items())}
    return canonical_json_hash(inventory)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentDataError(f"cannot load {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExperimentDataError(f"{label} must be a JSON object")
    return value


def load_experiment(
    manifest_path: Path, runner_config_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        _load_json(manifest_path, "experiment manifest"),
        _load_json(runner_config_path, "runner configuration"),
    )


def _resolve(config_path: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = config_path.parent / path
    return path.resolve()


def _unique_by(
    records: list[dict[str, Any]], field: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            errors.append(f"each {label} must be an object")
            continue
        value = record.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{label} requires a non-empty {field}")
            continue
        if value in indexed:
            errors.append(f"duplicate {label} {field}: {value}")
            continue
        indexed[value] = record
    return indexed


def _unique_strings(values: Any) -> TypeGuard[list[str]]:
    return (
        isinstance(values, list)
        and all(isinstance(value, str) for value in values)
        and len(values) == len(set(values))
    )


def validate_experiment(
    manifest: dict[str, Any],
    runner_config: dict[str, Any],
    *,
    runner_config_path: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    if manifest.get("schema_version") != "1.0":
        errors.append("experiment manifest schema_version must be 1.0")
    if runner_config.get("schema_version") != "1.0":
        errors.append("runner configuration schema_version must be 1.0")
    experiment_id = manifest.get("experiment_id")
    if not isinstance(experiment_id, str) or not SAFE_EXPERIMENT_ID.fullmatch(experiment_id):
        errors.append(
            f"unsafe experiment_id: {experiment_id!r} "
            f"(must match {SAFE_EXPERIMENT_ID.pattern})"
        )
    created_at = manifest.get("created_at")
    if not isinstance(created_at, str):
        errors.append("created_at must be an RFC 3339 timestamp")
    else:
        try:
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append("created_at must be an RFC 3339 timestamp")
    purpose = manifest.get("purpose")
    if purpose not in {"development", "release-candidate"}:
        errors.append("purpose must be development or release-candidate")
    expected_scope = (
        "organization-grade-candidate" if purpose == "release-candidate" else "development-only"
    )
    if manifest.get("claim_scope") != expected_scope:
        errors.append(f"{purpose} experiments require claim_scope {expected_scope}")
    estimand = manifest.get("estimand")
    if not isinstance(estimand, dict):
        errors.append("estimand must be an object")
    else:
        if estimand.get("target") not in {
            "fixed-benchmark-performance",
            "generalized-task-performance",
        }:
            errors.append("estimand target is invalid")
        if (
            not isinstance(estimand.get("population_definition"), str)
            or len(estimand["population_definition"].strip()) < 40
        ):
            errors.append("estimand population_definition is too vague")
        if estimand.get("unit") != "evaluation-case":
            errors.append("estimand unit must be evaluation-case")
        metrics = estimand.get("primary_metrics")
        if (
            not _unique_strings(metrics)
            or not metrics
            or any(
                metric not in {"activation_accuracy", "behavior_pass_rate"} for metric in metrics
            )
        ):
            errors.append("estimand primary_metrics are invalid")
    variants = manifest.get("variants")
    if not _unique_strings(variants) or set(variants) != VALID_VARIANTS or len(variants) != 3:
        errors.append("variants must contain each controlled cohort exactly once")
        variants = []
    replicate_ids = manifest.get("replicate_ids")
    if (
        not _unique_strings(replicate_ids)
        or not replicate_ids
        or any(
            not isinstance(item, str) or not SAFE_LOCAL_ID.fullmatch(item) for item in replicate_ids
        )
    ):
        errors.append("replicate_ids must be a non-empty unique string array")
        replicate_ids = []

    systems = manifest.get("systems")
    if not isinstance(systems, list) or not systems:
        errors.append("systems must be a non-empty array")
        systems = []
    system_map = _unique_by(systems, "system_id", "system", errors)
    configuration_hashes: dict[str, str] = {}
    independence_hashes: dict[str, str] = {}
    for system_id, system in system_map.items():
        if not SAFE_LOCAL_ID.fullmatch(system_id):
            errors.append(f"unsafe system_id: {system_id}")
        implementation = system.get("implementation")
        if not isinstance(implementation, dict) or not implementation:
            errors.append(f"{system_id}: implementation must be a non-empty object")
            continue
        if any(
            not isinstance(key, str)
            or not (value is None or isinstance(value, (str, int, float, bool)))
            for key, value in implementation.items()
        ):
            errors.append(f"{system_id}: implementation values must be scalar")
            continue
        configuration_hashes[system_id] = canonical_configuration_hash(implementation)
        independence_hashes[system_id] = canonical_configuration_hash(
            {
                field: implementation.get(field)
                for field in ("agent", "agent_version", "model", "model_version")
            }
        )
    duplicate_configurations = [
        digest
        for digest in set(configuration_hashes.values())
        if list(configuration_hashes.values()).count(digest) > 1
    ]
    if duplicate_configurations:
        errors.append("systems must use distinct pinned configurations")
    if len(set(independence_hashes.values())) != len(independence_hashes):
        errors.append("systems must use distinct agent/model identities")

    datasets = manifest.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        errors.append("datasets must be a non-empty array")
        datasets = []
    dataset_map = _unique_by(datasets, "dataset_id", "dataset", errors)
    for dataset_id in dataset_map:
        if not SAFE_LOCAL_ID.fullmatch(dataset_id):
            errors.append(f"unsafe dataset_id: {dataset_id}")
    configured_datasets = runner_config.get("datasets")
    if not isinstance(configured_datasets, list) or not configured_datasets:
        errors.append("runner configuration datasets must be a non-empty array")
        configured_datasets = []
    configured_dataset_map = _unique_by(configured_datasets, "dataset_id", "runner dataset", errors)
    if set(dataset_map) != set(configured_dataset_map):
        errors.append("runner datasets must exactly match manifest datasets")

    dataset_paths: dict[str, dict[str, Path]] = {}
    case_counts: dict[str, dict[str, int]] = {}
    dataset_digest_owners: dict[str, list[str]] = {}
    for dataset_id, dataset in dataset_map.items():
        if dataset.get("visibility") not in {"public", "held-out"}:
            errors.append(f"{dataset_id}: visibility must be public or held-out")
        configured = configured_dataset_map.get(dataset_id)
        if configured is None:
            continue
        dataset_paths[dataset_id] = {}
        case_counts[dataset_id] = {}
        loaded_parts: dict[str, dict[str, dict[str, Any]]] = {}
        for part in ("activation", "behavior"):
            value = configured.get(f"{part}_cases")
            if not isinstance(value, str) or not value:
                errors.append(f"{dataset_id}: missing {part}_cases path")
                continue
            path = _resolve(runner_config_path, value)
            dataset_paths[dataset_id][part] = path
            if not path.is_file():
                errors.append(f"{dataset_id}: {part} dataset does not exist")
                continue
            descriptor = dataset.get(part)
            if not isinstance(descriptor, dict):
                errors.append(f"{dataset_id}: missing {part} descriptor")
                continue
            digest = file_sha256(path)
            dataset_digest_owners.setdefault(digest, []).append(f"{dataset_id}:{part}")
            if descriptor.get("sha256") != digest:
                errors.append(f"{dataset_id}: {part} dataset hash mismatch")
            try:
                cases = load_case_map([path])
            except EvaluationDataError as exc:
                errors.append(f"{dataset_id}: invalid {part} dataset: {exc}")
                continue
            wrong_suite = sorted(
                case_id for case_id, case in cases.items() if case.get("suite") != part
            )
            if wrong_suite:
                errors.append(f"{dataset_id}: {part} dataset contains wrong-suite cases")
            versions = {case.get("dataset_version") for case in cases.values()}
            if versions != {manifest.get("dataset_version")}:
                errors.append(f"{dataset_id}: {part} dataset version mismatch")
            if descriptor.get("records") != len(cases):
                errors.append(f"{dataset_id}: {part} record count mismatch")
            case_counts[dataset_id][part] = len(cases)
            loaded_parts[part] = cases
        if len(loaded_parts) == 2 and set(loaded_parts["activation"]) & set(
            loaded_parts["behavior"]
        ):
            errors.append(f"{dataset_id}: activation and behavior case IDs overlap")
    for owners in dataset_digest_owners.values():
        owner_datasets = {owner.split(":", 1)[0] for owner in owners}
        if len(owner_datasets) > 1:
            errors.append(
                f"dataset content is reused across declared datasets: {', '.join(sorted(owners))}"
            )

    policy_path_value = runner_config.get("release_policy_path")
    policy: dict[str, Any] = {}
    policy_path = None
    if isinstance(policy_path_value, str) and policy_path_value:
        policy_path = _resolve(runner_config_path, policy_path_value)
        if not policy_path.is_file():
            errors.append("release policy does not exist")
        else:
            try:
                policy = _load_json(policy_path, "release policy")
            except ExperimentDataError as exc:
                errors.append(str(exc))
            policy_descriptor = manifest.get("release_policy")
            if not isinstance(policy_descriptor, dict):
                errors.append("manifest release_policy must be an object")
            else:
                if policy_descriptor.get("sha256") != file_sha256(policy_path):
                    errors.append("release policy hash mismatch")
                if policy_descriptor.get("version") != policy.get("version"):
                    errors.append("release policy version mismatch")
                if policy.get("dataset_version") != manifest.get("dataset_version"):
                    errors.append("release policy dataset version mismatch")
                required_fields = policy.get("required_implementation_fields", [])
                if isinstance(required_fields, list):
                    for system_id, system in system_map.items():
                        implementation = system.get("implementation", {})
                        missing = [
                            field
                            for field in required_fields
                            if implementation.get(field) in {None, ""}
                        ]
                        if missing:
                            errors.append(
                                f"{system_id}: missing pinned implementation fields {missing}"
                            )
    else:
        errors.append("runner configuration requires release_policy_path")

    configured_adapters = runner_config.get("adapters")
    if not isinstance(configured_adapters, list) or not configured_adapters:
        errors.append("runner configuration adapters must be a non-empty array")
        configured_adapters = []
    adapter_map = _unique_by(configured_adapters, "system_id", "adapter", errors)
    if set(adapter_map) != set(system_map):
        errors.append("runner adapters must exactly match manifest systems")
    for system_id, adapter in adapter_map.items():
        command = adapter.get("command")
        if (
            not isinstance(command, list)
            or not command
            or any(not isinstance(item, str) or not item for item in command)
        ):
            errors.append(f"{system_id}: adapter command must be a non-empty string array")
        else:
            joined_command = "\n".join(command)
            if any(pattern.search(joined_command) for _, pattern in SENSITIVE_CONTENT):
                errors.append(
                    f"{system_id}: adapter command contains a secret-like value; use the host environment"
                )

    skill_config = manifest.get("skills")
    for label, config_field in (
        ("with_skill", "current_skill_path"),
        ("previous_skill", "baseline_skill_path"),
    ):
        path_value = runner_config.get(config_field)
        descriptor = skill_config.get(label) if isinstance(skill_config, dict) else None
        if not isinstance(path_value, str) or not path_value:
            errors.append(f"runner configuration requires {config_field}")
            continue
        path = _resolve(runner_config_path, path_value)
        if not (path / "SKILL.md").is_file():
            errors.append(f"{config_field} must contain SKILL.md")
            continue
        if not isinstance(descriptor, dict):
            errors.append(f"manifest skills.{label} must be an object")
            continue
        try:
            observed_digest = runtime_sha256(path)
        except ExperimentDataError as exc:
            errors.append(str(exc))
            continue
        if descriptor.get("sha256") != observed_digest:
            errors.append(f"{label} runtime hash mismatch")
        try:
            version = (path / "VERSION").read_text(encoding="utf-8").strip()
        except OSError:
            errors.append(f"{label} runtime VERSION is missing")
        else:
            if descriptor.get("version") != version:
                errors.append(f"{label} runtime version mismatch")

    analysis = manifest.get("analysis")
    if not isinstance(analysis, dict):
        errors.append("analysis must be an object")
    else:
        if analysis.get("confidence_level") != 0.95:
            errors.append("confidence_level must be 0.95")
        if analysis.get("bootstrap_seed") != BOOTSTRAP_SEED:
            errors.append(f"bootstrap_seed must match the scorer seed {BOOTSTRAP_SEED}")
        exclusions = analysis.get("exclusions")
        if not isinstance(exclusions, list) or any(
            not isinstance(exclusion, str) or len(exclusion.strip()) < 10
            for exclusion in exclusions
        ):
            errors.append("analysis exclusions must be explicit string conditions")
        retry_policy = analysis.get("retry_policy")
        if not isinstance(retry_policy, dict):
            errors.append("analysis retry_policy must be an object")
        else:
            if (
                isinstance(retry_policy.get("maximum_attempts"), bool)
                or not isinstance(retry_policy.get("maximum_attempts"), int)
                or not 1 <= retry_policy["maximum_attempts"] <= 5
            ):
                errors.append("retry maximum_attempts must be between 1 and 5")
            if retry_policy.get("scored_attempt") != "highest-declared-attempt":
                errors.append("retry scored_attempt is invalid")
            allowed_reasons = retry_policy.get("allowed_reasons")
            if (
                not _unique_strings(allowed_reasons)
                or not allowed_reasons
                or any(
                    reason
                    not in {
                        "transport-error",
                        "provider-timeout",
                        "provider-unavailable",
                    }
                    for reason in allowed_reasons
                )
            ):
                errors.append("retry allowed_reasons are invalid")

    if purpose == "release-candidate":
        if (
            not isinstance(estimand, dict)
            or estimand.get("target") != "generalized-task-performance"
        ):
            errors.append("release candidate estimand must match the generalized-task scorer")
        minimum_systems = policy.get("minimum_systems", 1)
        minimum_replicates = policy.get("minimum_replicates", 1)
        if len(system_map) < minimum_systems:
            errors.append(
                f"release candidate has {len(system_map)} systems; policy requires {minimum_systems}"
            )
        if len(replicate_ids) < minimum_replicates:
            errors.append(
                f"release candidate has {len(replicate_ids)} replicates; policy requires {minimum_replicates}"
            )
        if not any(dataset.get("visibility") == "held-out" for dataset in dataset_map.values()):
            errors.append("release candidate requires a held-out dataset")

    limits = runner_config.get("limits")
    if not isinstance(limits, dict):
        errors.append("runner limits must be an object")
    else:
        for field in (
            "max_workers",
            "timeout_seconds",
            "max_input_bytes",
            "max_output_bytes",
            "max_stderr_bytes",
        ):
            value = limits.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                errors.append(f"runner limit {field} must be a positive integer")
        if isinstance(limits.get("max_workers"), int) and limits["max_workers"] > 16:
            errors.append("runner max_workers cannot exceed 16")

    return {
        "errors": errors,
        "manifest_sha256": canonical_json_hash(manifest),
        "configuration_hashes": configuration_hashes,
        "system_map": system_map,
        "adapter_map": adapter_map,
        "dataset_paths": dataset_paths,
        "case_counts": case_counts,
        "policy_path": policy_path,
    }


def execution_jobs(manifest: dict[str, Any], validation: dict[str, Any]) -> list[dict[str, Any]]:
    if validation["errors"]:
        raise ExperimentDataError("cannot plan an invalid experiment")
    jobs: list[dict[str, Any]] = []
    for dataset in manifest["datasets"]:
        dataset_id = dataset["dataset_id"]
        for part in ("activation", "behavior"):
            for system in manifest["systems"]:
                system_id = system["system_id"]
                for variant in manifest["variants"]:
                    for replicate_id in manifest["replicate_ids"]:
                        jobs.append(
                            {
                                "dataset_id": dataset_id,
                                "suite": part,
                                "system_id": system_id,
                                "variant": variant,
                                "replicate_id": replicate_id,
                                "cases_path": validation["dataset_paths"][dataset_id][part],
                                "implementation": system["implementation"],
                                "configuration_hash": validation["configuration_hashes"][system_id],
                                "adapter_command": validation["adapter_map"][system_id]["command"],
                            }
                        )
    return jobs


def job_relative_output(job: dict[str, Any]) -> Path:
    return Path(
        job["dataset_id"],
        job["system_id"],
        job["variant"],
        job["replicate_id"],
        f"{job['suite']}.jsonl",
    )


def audit_result_file(
    manifest: dict[str, Any],
    job: dict[str, Any],
    output_path: Path,
) -> list[str]:
    errors: list[str] = []
    try:
        cases = load_case_map([job["cases_path"]])
        results = read_jsonl(output_path)
    except EvaluationDataError as exc:
        return [str(exc)]
    expected_ids = list(cases)
    observed_ids = [result.get("case_id") for result in results]
    if observed_ids != expected_ids:
        errors.append("result case IDs do not match the frozen dataset order")
    for result in results:
        result_errors = validate_result(result, cases)
        errors.extend(f"{result.get('case_id', '?')}: {error}" for error in result_errors)
        expected_identity = {
            "run_id": manifest["experiment_id"],
            "system_id": job["system_id"],
            "variant": job["variant"],
            "replicate_id": job["replicate_id"],
            "dataset_version": manifest["dataset_version"],
            "configuration_hash": job["configuration_hash"],
        }
        if "execution_attempt" in job:
            expected_identity["attempt"] = job["execution_attempt"]
        for field, expected in expected_identity.items():
            if result.get(field) != expected:
                errors.append(f"{result.get('case_id', '?')}: {field} differs from experiment")
        if result.get("implementation") != job["implementation"]:
            errors.append(
                f"{result.get('case_id', '?')}: implementation differs from preregistration"
            )
    return errors
