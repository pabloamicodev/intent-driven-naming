"""Loading, validation, repeated-run scoring, and release-policy primitives."""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from collections.abc import Iterable
from copy import deepcopy
from pathlib import Path
from typing import Any

from harness.routing import allowed_behavior_resources, loaded_profile_count

VALID_GRADES = {"pass", "fail", "not-applicable"}
QUALITY_VARIANTS = {"with-skill", "without-skill"}
VALID_VARIANTS = {*QUALITY_VARIANTS, "previous-skill"}
VALID_DECISIONS = {"keep", "rename", "map", "migrate", "defer", "not-applicable"}
VALID_DIFFICULTIES = {"easy", "standard", "edge", "adversarial"}
VALID_MODES = {"generation", "audit", "refactor"}
VALID_RISKS = {
    "internal", "cross-module", "external", "dynamic", "generated", "stateful", "unknown"
}
RESULT_FIELDS = {
    "schema_version",
    "protocol_version",
    "dataset_version",
    "run_id",
    "system_id",
    "configuration_hash",
    "replicate_id",
    "attempt",
    "case_id",
    "variant",
    "status",
    "selected_skill",
    "output_text",
    "artifact_path",
    "artifact_bundle",
    "loaded_resources",
    "observed_decisions",
    "invariant_grades",
    "grader_notes",
    "usage",
    "implementation",
    "error",
}


class EvaluationDataError(ValueError):
    """Raised when an evaluation artifact violates the local protocol."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationDataError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise EvaluationDataError(f"{path}:{line_number}: each line must be a JSON object")
        records.append(record)
    return records


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records
    )
    path.write_text(content, encoding="utf-8", newline="\n")


def canonical_configuration_hash(configuration: dict[str, Any]) -> str:
    payload = json.dumps(configuration, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_case(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    case_id = case.get("id")
    suite = case.get("suite")
    if case.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if not isinstance(case.get("dataset_version"), str) or not case["dataset_version"].strip():
        errors.append("dataset_version must be non-empty")
    if not isinstance(case_id, str) or len(case_id) != 3 or case_id[0] not in "TB":
        errors.append("id must match TNN or BNN")
    if suite not in {"activation", "behavior"}:
        errors.append("suite must be activation or behavior")
    for field in ("title", "prompt", "locale"):
        if not isinstance(case.get(field), str) or not case[field].strip():
            errors.append(f"{field} must be non-empty")
    if case.get("difficulty") not in VALID_DIFFICULTIES:
        errors.append("difficulty is invalid")
    tags = case.get("tags")
    if not isinstance(tags, list) or not tags or any(not isinstance(tag, str) for tag in tags):
        errors.append("tags must be a non-empty string array")
    elif len(tags) != len(set(tags)):
        errors.append("tags must be unique")
    if suite == "activation":
        if not isinstance(case.get("expected_activation"), bool):
            errors.append("activation cases require expected_activation")
        if not isinstance(case.get("rationale"), str) or not case["rationale"].strip():
            errors.append("activation cases require rationale")
    if suite == "behavior":
        if case.get("mode") not in VALID_MODES:
            errors.append("behavior mode is invalid")
        if case.get("contract_risk") not in VALID_RISKS:
            errors.append("behavior contract_risk is invalid")
        languages = case.get("languages")
        if not isinstance(languages, list) or not languages or any(
            not isinstance(language, str) or not language for language in languages
        ):
            errors.append("behavior languages must be a non-empty string array")
        decisions = case.get("expected_decisions")
        if not isinstance(decisions, list) or not decisions or any(
            decision not in VALID_DECISIONS for decision in decisions
        ):
            errors.append("behavior expected_decisions are invalid")
        elif len(decisions) != len(set(decisions)):
            errors.append("behavior expected_decisions must be unique")
        invariants = case.get("invariants")
        if not isinstance(invariants, list) or not invariants:
            errors.append("behavior cases require invariants")
        else:
            invariant_ids: set[str] = set()
            for invariant in invariants:
                if not isinstance(invariant, dict):
                    errors.append("each invariant must be an object")
                    continue
                invariant_id = invariant.get("id")
                if not isinstance(invariant_id, str) or not invariant_id:
                    errors.append("invariant id must be non-empty")
                elif invariant_id in invariant_ids:
                    errors.append(f"duplicate invariant id {invariant_id}")
                invariant_ids.add(invariant_id)
                if invariant.get("severity") not in {"critical", "major", "minor"}:
                    errors.append(f"{invariant_id}: invalid severity")
                if invariant.get("grading") not in {"deterministic", "semantic", "human"}:
                    errors.append(f"{invariant_id}: invalid grading")
                if not isinstance(invariant.get("description"), str) or not invariant["description"].strip():
                    errors.append(f"{invariant_id}: description must be non-empty")
    return errors


def _valid_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def validate_result(result: dict[str, Any], cases: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    unknown_fields = set(result) - RESULT_FIELDS
    if unknown_fields:
        errors.append(f"unknown result fields: {', '.join(sorted(unknown_fields))}")
    case_id = result.get("case_id")
    if result.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if result.get("protocol_version") != 1:
        errors.append("protocol_version must be 1")
    if not isinstance(result.get("run_id"), str) or not result["run_id"].strip():
        errors.append("run_id must be non-empty")
    if case_id not in cases:
        errors.append(f"unknown case_id {case_id}")
        return errors
    case = cases[case_id]
    if result.get("dataset_version") != case["dataset_version"]:
        errors.append("dataset_version does not match the case")
    for field in ("system_id", "replicate_id"):
        if not isinstance(result.get(field), str) or not result[field].strip():
            errors.append(f"{field} must be non-empty")
    if (
        not isinstance(result.get("configuration_hash"), str)
        or len(result["configuration_hash"]) != 64
        or any(character not in "0123456789abcdef" for character in result["configuration_hash"])
    ):
        errors.append("configuration_hash must be a lowercase SHA-256 hex string")
    if (
        isinstance(result.get("attempt"), bool)
        or not isinstance(result.get("attempt"), int)
        or result["attempt"] < 1
    ):
        errors.append("attempt must be an integer of at least 1")
    if result.get("variant") not in VALID_VARIANTS:
        errors.append("variant must be with-skill, previous-skill, or without-skill")
    if result.get("status") not in {"completed", "failed", "skipped"}:
        errors.append("status must be completed, failed, or skipped")
    if result.get("status") == "failed" and (
        not isinstance(result.get("error"), str) or not result["error"].strip()
    ):
        errors.append("failed result requires a non-empty error")
    if result.get("selected_skill") is not None and not isinstance(result.get("selected_skill"), bool):
        errors.append("selected_skill must be boolean or null")
    for field in ("output_text", "artifact_path", "grader_notes", "error"):
        if result.get(field) is not None and not isinstance(result.get(field), str):
            errors.append(f"{field} must be string or null")
    resources = result.get("loaded_resources")
    if resources is not None and (
        not isinstance(resources, list)
        or any(not isinstance(resource, str) or not resource for resource in resources)
        or len(resources) != len(set(resources))
    ):
        errors.append("loaded_resources must be a unique string array")
    elif isinstance(resources, list) and any(
        Path(resource).is_absolute() or ".." in Path(resource).parts for resource in resources
    ):
        errors.append("loaded_resources must use safe relative paths")
    decisions = result.get("observed_decisions")
    if decisions is not None and (
        not isinstance(decisions, list)
        or any(decision not in VALID_DECISIONS for decision in decisions)
        or len(decisions) != len(set(decisions))
    ):
        errors.append("observed_decisions are invalid")
    bundle = result.get("artifact_bundle")
    if bundle is not None:
        if not isinstance(bundle, dict):
            errors.append("artifact_bundle must be an object")
        else:
            allowed = {"format", "path", "sha256", "verifier_report_path"}
            if set(bundle) - allowed:
                errors.append("artifact_bundle contains unknown fields")
            if bundle.get("format") not in {"unified-diff", "directory", "none"}:
                errors.append("artifact_bundle.format is invalid")
            if bundle.get("path") is not None and not isinstance(bundle.get("path"), str):
                errors.append("artifact_bundle.path must be string or null")
            digest = bundle.get("sha256")
            if digest is not None and (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                errors.append("artifact_bundle.sha256 must be lowercase SHA-256 hex")
    usage = result.get("usage")
    if usage is not None:
        if not isinstance(usage, dict):
            errors.append("usage must be an object")
        else:
            integer_metrics = {
                "input_tokens", "output_tokens", "skill_context_words", "turns", "tool_calls"
            }
            allowed_metrics = integer_metrics | {"latency_ms", "cost_usd"}
            unknown_usage = set(usage) - allowed_metrics
            if unknown_usage:
                errors.append(f"usage has unknown fields: {', '.join(sorted(unknown_usage))}")
            for key in allowed_metrics:
                value = usage.get(key)
                expected_types = (int,) if key in integer_metrics else (int, float)
                if value is not None and (
                    isinstance(value, bool) or not isinstance(value, expected_types) or value < 0
                ):
                    expected = "integer" if key in integer_metrics else "number"
                    errors.append(f"usage.{key} must be a non-negative {expected} or null")
    implementation = result.get("implementation")
    if implementation is not None and (
        not isinstance(implementation, dict)
        or any(not isinstance(key, str) or not _valid_scalar(value) for key, value in implementation.items())
    ):
        errors.append("implementation keys and values must be scalar")
    grades = result.get("invariant_grades", {})
    if not isinstance(grades, dict):
        errors.append("invariant_grades must be an object")
    elif case["suite"] == "behavior":
        valid_ids = {item["id"] for item in case["invariants"]}
        unknown = set(grades) - valid_ids
        if unknown:
            errors.append(f"unknown invariant grades: {', '.join(sorted(unknown))}")
        invalid_values = {value for value in grades.values() if value not in VALID_GRADES}
        if invalid_values:
            errors.append(f"invalid grade values: {', '.join(sorted(invalid_values))}")
    if result.get("status") == "completed" and (suite := case.get("suite")):
        if suite == "activation" and not isinstance(result.get("selected_skill"), bool):
            errors.append("completed activation result requires selected_skill")
        if suite == "behavior":
            output_text = result.get("output_text")
            usable_bundle = isinstance(bundle, dict) and bundle.get("format") != "none"
            if (not isinstance(output_text, str) or not output_text.strip()) and not usable_bundle:
                errors.append("completed behavior result requires output_text or artifact_bundle")
    return errors


def load_case_map(paths: Iterable[Path]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    versions: set[str] = set()
    for path in paths:
        for case in read_jsonl(path):
            errors = validate_case(case)
            if errors:
                raise EvaluationDataError(f"{path}:{case.get('id', '?')}: {'; '.join(errors)}")
            case_id = case["id"]
            if case_id in cases:
                raise EvaluationDataError(f"duplicate case id {case_id}")
            cases[case_id] = case
            versions.add(case["dataset_version"])
    if len(versions) > 1:
        raise EvaluationDataError(f"mixed dataset versions: {sorted(versions)}")
    return cases


def _safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    if total == 0:
        return None
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return [round(max(0.0, center - margin), 6), round(min(1.0, center + margin), 6)]


def _paired_difference(outcomes: dict[Any, dict[str, int]]) -> dict[str, Any] | None:
    paired = [
        (key, variants["with-skill"] - variants["without-skill"])
        for key, variants in outcomes.items()
        if QUALITY_VARIANTS.issubset(variants)
    ]
    differences = [difference for _, difference in paired]
    if not differences:
        return None
    differences_by_case: dict[Any, list[int]] = defaultdict(list)
    for key, difference in paired:
        case_id = key[1] if isinstance(key, tuple) and len(key) > 1 else key
        differences_by_case[case_id].append(difference)
    case_ids = sorted(differences_by_case, key=str)
    mean = sum(differences) / len(differences)
    randomizer = random.Random(20260821)
    bootstrap_means: list[float] = []
    for _ in range(10_000):
        sampled_differences = [
            difference
            for _ in case_ids
            for difference in differences_by_case[randomizer.choice(case_ids)]
        ]
        bootstrap_means.append(sum(sampled_differences) / len(sampled_differences))
    bootstrap_means.sort()
    lower_index = int(0.025 * (len(bootstrap_means) - 1))
    upper_index = int(0.975 * (len(bootstrap_means) - 1))
    return {
        "method": "paired-case-cluster-percentile-bootstrap-95",
        "bootstrap_samples": 10_000,
        "bootstrap_seed": 20260821,
        "clusters": len(case_ids),
        "matched_pairs": len(differences),
        "candidate_better": sum(difference > 0 for difference in differences),
        "baseline_better": sum(difference < 0 for difference in differences),
        "ties": sum(difference == 0 for difference in differences),
        "delta": round(mean, 6),
        "confidence_interval_95": [
            round(bootstrap_means[lower_index], 6),
            round(bootstrap_means[upper_index], 6),
        ],
    }


def _identity(result: dict[str, Any]) -> tuple[str, str, str, int]:
    return (
        result.get("system_id", "legacy"),
        result["variant"],
        result.get("replicate_id", "r1"),
        result.get("attempt", 1),
    )


def _cohort_key(system_id: str, variant: str) -> str:
    return f"{system_id}::{variant}"


def _confusion_metrics(counts: dict[str, int]) -> dict[str, Any]:
    tp, tn, fp, fn = (counts.get(key, 0) for key in ("tp", "tn", "fp", "fn"))
    total = tp + tn + fp + fn
    precision = _safe_ratio(tp, tp + fp)
    recall = _safe_ratio(tp, tp + fn)
    specificity = _safe_ratio(tn, tn + fp)
    return {
        **counts,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "false_positive_rate": _safe_ratio(fp, fp + tn),
        "balanced_accuracy": round((recall + specificity) / 2, 6)
        if recall is not None and specificity is not None
        else None,
        "accuracy": _safe_ratio(tp + tn, total),
        "accuracy_confidence_interval_95": _wilson_interval(tp + tn, total),
        "classified_results": total,
    }


def score_results(
    cases: dict[str, dict[str, Any]],
    results: list[dict[str, Any]],
    *,
    require_complete: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    attempts: dict[tuple[str, str, str, str, int], dict[str, Any]] = {}
    for result in results:
        result_errors = validate_result(result, cases)
        if result_errors:
            errors.extend(f"{result.get('case_id', '?')}: {error}" for error in result_errors)
            continue
        system_id, variant, replicate_id, attempt = _identity(result)
        key = (system_id, variant, replicate_id, result["case_id"], attempt)
        if key in attempts:
            errors.append(f"duplicate result attempt for {key}")
            continue
        attempts[key] = result

    final_results: list[dict[str, Any]] = []
    attempt_groups: dict[tuple[str, str, str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for (system_id, variant, replicate_id, case_id, attempt), result in attempts.items():
        attempt_groups[(system_id, variant, replicate_id, case_id)].append((attempt, result))
    for grouped_attempts in attempt_groups.values():
        final_results.append(max(grouped_attempts, key=lambda item: item[0])[1])

    cohorts: dict[str, dict[str, Any]] = {}
    completion: dict[str, Any] = {}
    activation_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "skipped": 0}
    )
    activation_slice_counts: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: {"tp": 0, "tn": 0, "fp": 0, "fn": 0})
    )
    behavior_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "pass": 0,
            "fail": 0,
            "not-applicable": 0,
            "ungraded": 0,
            "critical_failures": 0,
            "critical_ungraded": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "ungraded_cases": 0,
        }
    )
    tag_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "fail": 0})
    decision_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "graded_cases": 0,
            "exact_matches": 0,
            "ungraded_cases": 0,
            "by_expected": defaultdict(lambda: {"cases": 0, "exact_matches": 0}),
            "confusion": defaultdict(lambda: defaultdict(int)),
        }
    )
    usage_values: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "completed_results": 0,
            "input_tokens": [],
            "output_tokens": [],
            "latency_ms": [],
            "cost_usd": [],
            "skill_context_words": [],
            "turns": [],
            "tool_calls": [],
            "identity_complete": 0,
        }
    )
    routed_resources = {"SKILL.md", "references/naming-model.md"}
    routes_path = Path(__file__).resolve().parents[1] / "specification" / "routes.json"
    try:
        route_data = json.loads(routes_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        route_data = {}
    routed_resources.update(route_data.get("always", []))
    for group_name in ("conditional_core", "modes", "features", "profiles"):
        for paths in route_data.get(group_name, {}).values():
            routed_resources.update(paths)
    resource_values: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "completed_results": 0,
            "reported_results": 0,
            "core_expected_results": 0,
            "core_complete_results": 0,
            "unexpected_activation_resource_results": 0,
            "total_resource_loads": 0,
            "unknown_resources": Counter(),
            "unnecessary_resources": Counter(),
            "overloaded_profile_results": 0,
        }
    )
    implementation_fields: dict[str, Counter[str]] = defaultdict(Counter)
    behavior_review_counts: dict[str, list[int]] = defaultdict(list)
    completed_by_replicate: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    paired_outcomes: dict[str, dict[str, dict[Any, dict[str, int]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict))
    )

    for result in final_results:
        system_id, variant, replicate_id, _ = _identity(result)
        cohort = _cohort_key(system_id, variant)
        cohorts.setdefault(
            cohort,
            {"system_id": system_id, "variant": variant, "replicates": set()},
        )["replicates"].add(replicate_id)
        case = cases[result["case_id"]]
        if result["status"] != "completed":
            if case["suite"] == "activation":
                activation_counts[cohort]["skipped"] += 1
            continue
        completed_by_replicate[(system_id, variant, replicate_id)].add(case["id"])
        usage_values[cohort]["completed_results"] += 1
        identity_fields = (
            "dataset_version",
            "system_id",
            "configuration_hash",
            "replicate_id",
            "attempt",
        )
        if all(field in result and result[field] not in {None, ""} for field in identity_fields):
            usage_values[cohort]["identity_complete"] += 1
        for metric in (
            "input_tokens", "output_tokens", "latency_ms", "cost_usd",
            "skill_context_words", "turns", "tool_calls",
        ):
            value = (result.get("usage") or {}).get(metric)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                usage_values[cohort][metric].append(value)
        resource_values[cohort]["completed_results"] += 1
        resources = result.get("loaded_resources")
        expects_core = variant != "without-skill" and (
            case["suite"] == "behavior" or case.get("expected_activation") is True
        )
        if expects_core:
            resource_values[cohort]["core_expected_results"] += 1
        if isinstance(resources, list):
            resource_values[cohort]["reported_results"] += 1
            resource_values[cohort]["total_resource_loads"] += len(resources)
            if expects_core and {"SKILL.md", "references/naming-model.md"}.issubset(resources):
                resource_values[cohort]["core_complete_results"] += 1
            if (
                variant != "without-skill"
                and case["suite"] == "activation"
                and case.get("expected_activation") is False
                and resources
            ):
                resource_values[cohort]["unexpected_activation_resource_results"] += 1
            resource_values[cohort]["unknown_resources"].update(
                resource for resource in resources if resource not in routed_resources
            )
            if variant != "without-skill" and case["suite"] == "behavior":
                resource_set = set(resources)
                allowed = allowed_behavior_resources(case, route_data)
                resource_values[cohort]["unnecessary_resources"].update(
                    resource for resource in resource_set if resource in routed_resources - allowed
                )
                if loaded_profile_count(resource_set, route_data) > 2:
                    resource_values[cohort]["overloaded_profile_results"] += 1
        for field, value in (result.get("implementation") or {}).items():
            if value is not None and value != "":
                implementation_fields[cohort][field] += 1

        if case["suite"] == "activation":
            selected = result.get("selected_skill")
            if not isinstance(selected, bool):
                errors.append(f"{case['id']}: completed activation result requires selected_skill")
                continue
            expected = case["expected_activation"]
            bucket = "tp" if expected and selected else "tn" if not expected and not selected else "fp" if selected else "fn"
            activation_counts[cohort][bucket] += 1
            paired_outcomes[system_id]["activation_accuracy"][(replicate_id, case["id"])][
                variant
            ] = int(selected == expected)
            for slice_name in (f"difficulty:{case['difficulty']}", f"locale:{case['locale']}"):
                activation_slice_counts[cohort][slice_name][bucket] += 1
            continue

        grades = result.get("invariant_grades", {})
        review_count = (result.get("implementation") or {}).get("review_count", 0)
        behavior_review_counts[cohort].append(
            review_count
            if isinstance(review_count, int) and not isinstance(review_count, bool) and review_count >= 0
            else 0
        )
        case_has_fail = False
        case_has_ungraded = False
        for invariant in case["invariants"]:
            grade = grades.get(invariant["id"])
            if grade is None:
                behavior_counts[cohort]["ungraded"] += 1
                case_has_ungraded = True
                if invariant["severity"] == "critical":
                    behavior_counts[cohort]["critical_ungraded"] += 1
                continue
            behavior_counts[cohort][grade] += 1
            if grade in {"pass", "fail"}:
                paired_outcomes[system_id]["behavior_pass_rate"][(
                    replicate_id,
                    case["id"],
                    invariant["id"],
                )][variant] = int(grade == "pass")
            if grade == "fail":
                case_has_fail = True
                if invariant["severity"] == "critical":
                    behavior_counts[cohort]["critical_failures"] += 1
            if grade in {"pass", "fail"}:
                for tag in case["tags"]:
                    tag_stats[f"{cohort}:{tag}"][grade] += 1
        if case_has_ungraded:
            behavior_counts[cohort]["ungraded_cases"] += 1
        elif case_has_fail:
            behavior_counts[cohort]["failed_cases"] += 1
        else:
            behavior_counts[cohort]["passed_cases"] += 1

        observed = result.get("observed_decisions")
        if not isinstance(observed, list):
            decision_stats[cohort]["ungraded_cases"] += 1
        else:
            expected_set = set(case["expected_decisions"])
            observed_set = set(observed)
            exact = expected_set == observed_set
            decision_stats[cohort]["graded_cases"] += 1
            decision_stats[cohort]["exact_matches"] += int(exact)
            for expected_decision in expected_set:
                decision_stats[cohort]["by_expected"][expected_decision]["cases"] += 1
                decision_stats[cohort]["by_expected"][expected_decision]["exact_matches"] += int(exact)
            if len(expected_set) == 1 and len(observed_set) == 1:
                decision_stats[cohort]["confusion"][next(iter(expected_set))][next(iter(observed_set))] += 1

    for metadata in cohorts.values():
        metadata["replicates"] = sorted(metadata["replicates"])
        metadata["replicate_count"] = len(metadata["replicates"])
    for cohort, metadata in cohorts.items():
        for replicate_id in metadata["replicates"]:
            completed_ids = completed_by_replicate.get(
                (metadata["system_id"], metadata["variant"], replicate_id), set()
            )
            incomplete_ids = sorted(set(cases) - completed_ids)
            key = f"{cohort}::{replicate_id}"
            completion[key] = {
                "cohort": cohort,
                "replicate_id": replicate_id,
                "expected_cases": len(cases),
                "completed_cases": len(completed_ids),
                "incomplete_case_ids": incomplete_ids,
                "complete": not incomplete_ids,
            }
            if require_complete and incomplete_ids:
                errors.append(f"{key}: {len(incomplete_ids)} cases are missing, failed, or skipped")
    if require_complete and not cohorts:
        errors.append("complete scoring requires at least one result cohort")

    activation_report = {
        cohort: _confusion_metrics(counts) for cohort, counts in sorted(activation_counts.items())
    }
    activation_slices = {
        cohort: {
            slice_name: _confusion_metrics(counts)
            for slice_name, counts in sorted(slices.items())
        }
        for cohort, slices in sorted(activation_slice_counts.items())
    }
    behavior_report: dict[str, Any] = {}
    for cohort, counts in sorted(behavior_counts.items()):
        graded = counts["pass"] + counts["fail"]
        graded_cases = counts["passed_cases"] + counts["failed_cases"]
        behavior_report[cohort] = {
            **counts,
            "pass_rate": _safe_ratio(counts["pass"], graded),
            "pass_rate_confidence_interval_95": _wilson_interval(counts["pass"], graded),
            "case_pass_rate": _safe_ratio(counts["passed_cases"], graded_cases),
            "hard_gate_passed": counts["critical_failures"] == 0
            and counts["critical_ungraded"] == 0,
        }
    decision_report: dict[str, Any] = {}
    for cohort, stats in sorted(decision_stats.items()):
        decision_report[cohort] = {
            "graded_cases": stats["graded_cases"],
            "exact_matches": stats["exact_matches"],
            "ungraded_cases": stats["ungraded_cases"],
            "exact_match_rate": _safe_ratio(stats["exact_matches"], stats["graded_cases"]),
            "by_expected": {
                key: {
                    **value,
                    "exact_match_rate": _safe_ratio(value["exact_matches"], value["cases"]),
                }
                for key, value in sorted(stats["by_expected"].items())
            },
            "single_label_confusion": {
                expected: dict(sorted(actual.items()))
                for expected, actual in sorted(stats["confusion"].items())
            },
        }
    tag_report = {
        key: {**counts, "pass_rate": _safe_ratio(counts["pass"], counts["pass"] + counts["fail"])}
        for key, counts in sorted(tag_stats.items())
    }
    usage_report: dict[str, Any] = {}
    for cohort, values in sorted(usage_values.items()):
        usage_report[cohort] = {
            "completed_results": values["completed_results"],
            "identity_complete_results": values["identity_complete"],
        }
        for metric in (
            "input_tokens", "output_tokens", "latency_ms", "cost_usd",
            "skill_context_words", "turns", "tool_calls",
        ):
            samples = values[metric]
            usage_report[cohort][metric] = {
                "reported_results": len(samples),
                "total": round(sum(samples), 6) if samples else None,
                "mean": round(sum(samples) / len(samples), 6) if samples else None,
            }
    resource_report = {
        cohort: {
            "completed_results": values["completed_results"],
            "reported_results": values["reported_results"],
            "reporting_rate": _safe_ratio(values["reported_results"], values["completed_results"]),
            "core_expected_results": values["core_expected_results"],
            "core_complete_results": values["core_complete_results"],
            "core_complete_rate": _safe_ratio(
                values["core_complete_results"], values["core_expected_results"]
            ),
            "unexpected_activation_resource_results": values[
                "unexpected_activation_resource_results"
            ],
            "total_resource_loads": values["total_resource_loads"],
            "mean_resources_per_result": _safe_ratio(
                values["total_resource_loads"], values["reported_results"]
            ),
            "unknown_resources": dict(sorted(values["unknown_resources"].items())),
            "unnecessary_resources": dict(
                sorted(values["unnecessary_resources"].items())
            ),
            "overloaded_profile_results": values["overloaded_profile_results"],
        }
        for cohort, values in sorted(resource_values.items())
    }
    implementation_report = {
        cohort: {
            "completed_results": usage_report.get(cohort, {}).get("completed_results", 0),
            "field_presence": dict(sorted(implementation_fields[cohort].items())),
        }
        for cohort in sorted(set(usage_report) | set(implementation_fields))
    }
    retry_report = {
        "result_attempts": len(attempts),
        "final_results": len(final_results),
        "retried_case_runs": sum(len(group) > 1 for group in attempt_groups.values()),
    }
    review_coverage = {
        cohort: {
            "behavior_results": len(counts),
            "minimum_review_count": min(counts, default=0),
            "fully_reviewed_results": sum(count > 0 for count in counts),
        }
        for cohort, counts in sorted(behavior_review_counts.items())
    }
    paired_comparisons = {
        system_id: {
            metric: _paired_difference(outcomes)
            for metric, outcomes in sorted(metrics.items())
        }
        for system_id, metrics in sorted(paired_outcomes.items())
    }
    return {
        "schema_version": "2.0",
        "dataset_version": next(iter({case["dataset_version"] for case in cases.values()}), None),
        "require_complete": require_complete,
        "errors": errors,
        "cohorts": dict(sorted(cohorts.items())),
        "completion": dict(sorted(completion.items())),
        "activation": activation_report,
        "activation_by_slice": activation_slices,
        "behavior": behavior_report,
        "decisions": decision_report,
        "by_tag": tag_report,
        "usage": usage_report,
        "resource_loading": resource_report,
        "implementation_metadata": implementation_report,
        "review_coverage": review_coverage,
        "paired_comparisons": paired_comparisons,
        "retries": retry_report,
        "hard_gate_passed": not errors
        and all(item["hard_gate_passed"] for item in behavior_report.values()),
    }


def apply_release_policy(report: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    evaluated = deepcopy(report)
    violations: list[str] = []
    observations: dict[str, Any] = {}
    if not isinstance(policy, dict):
        evaluated["policy"] = {
            "name": None,
            "version": None,
            "violations": ["release policy must be a JSON object"],
            "passed": False,
        }
        evaluated["hard_gate_passed"] = False
        return evaluated
    if policy.get("schema_version") != "2.0":
        violations.append("release policy schema_version must be 2.0")
    if policy.get("dataset_version") != report.get("dataset_version"):
        violations.append("release policy dataset_version does not match the results")
    required_variants = policy.get("required_variants", [])
    if not isinstance(required_variants, list) or set(required_variants) != VALID_VARIANTS:
        violations.append("release policy must require with-skill, previous-skill, and without-skill")
        required_variants = []
    gated_variant = policy.get("gated_variant")
    if gated_variant not in VALID_VARIANTS:
        violations.append("release policy gated_variant is invalid")
    systems = sorted({metadata["system_id"] for metadata in report.get("cohorts", {}).values()})
    if not systems:
        violations.append("release policy requires at least one system")
    minimum_replicates = policy.get("minimum_replicates", 1)
    if isinstance(minimum_replicates, bool) or not isinstance(minimum_replicates, int) or minimum_replicates < 1:
        violations.append("minimum_replicates must be a positive integer")
        minimum_replicates = 1
    activation_policy = policy.get("activation", {})
    behavior_policy = policy.get("behavior", {})
    comparison_policy = policy.get("comparison", {})
    if not isinstance(comparison_policy, dict) or comparison_policy.get(
        "baseline_variant"
    ) != "without-skill":
        violations.append("comparison baseline_variant must be without-skill")
        comparison_policy = {}
    required_fields = policy.get("required_implementation_fields", [])
    if not isinstance(required_fields, list) or any(not isinstance(field, str) for field in required_fields):
        violations.append("required_implementation_fields must be a string array")
        required_fields = []
    efficiency_policy = policy.get("efficiency", {})
    if not isinstance(efficiency_policy, dict) or efficiency_policy.get(
        "comparison_variant"
    ) != "previous-skill":
        violations.append("efficiency comparison_variant must be previous-skill")
        efficiency_policy = {}
    required_usage_fields = efficiency_policy.get("required_usage_fields", [])
    if not isinstance(required_usage_fields, list) or any(
        not isinstance(field, str) for field in required_usage_fields
    ):
        violations.append("efficiency required_usage_fields must be a string array")
        required_usage_fields = []

    review_policy = policy.get("review")
    if isinstance(review_policy, dict):
        agreement = report.get("review_agreement")
        if not isinstance(agreement, dict):
            violations.append("review agreement report is required")
        else:
            expected_reviewed_candidates = sum(
                report.get("review_coverage", {})
                .get(_cohort_key(system_id, variant), {})
                .get("behavior_results", 0)
                for system_id in systems
                for variant in required_variants
            )
            if agreement.get("reviewed_candidates") != expected_reviewed_candidates:
                violations.append(
                    "reviewed_candidates "
                    f"{agreement.get('reviewed_candidates')} does not match expected "
                    f"{expected_reviewed_candidates}"
                )
            minimum_reviews = review_policy.get("minimum_reviews_per_candidate")
            if (
                isinstance(minimum_reviews, int)
                and not isinstance(minimum_reviews, bool)
                and agreement.get("minimum_reviews_per_candidate", 0) < minimum_reviews
            ):
                violations.append(
                    "review minimum_reviews_per_candidate "
                    f"{agreement.get('minimum_reviews_per_candidate')} is below {minimum_reviews}"
                )
            for policy_name, report_name in (
                ("minimum_raw_grade_agreement", "raw_grade_agreement"),
                (
                    "minimum_chance_corrected_grade_agreement",
                    "chance_corrected_grade_agreement",
                ),
                ("minimum_decision_set_agreement", "decision_set_agreement"),
            ):
                minimum = review_policy.get(policy_name)
                observed = agreement.get(report_name)
                if minimum is not None and (observed is None or observed < minimum):
                    violations.append(f"review {report_name} {observed} is below {minimum}")

    pairwise_policy = policy.get("pairwise")
    if isinstance(pairwise_policy, dict):
        pairwise = report.get("pairwise_report")
        if not isinstance(pairwise, dict):
            violations.append("pairwise report is required")
        else:
            expected_pairs = sum(
                report.get("review_coverage", {})
                .get(_cohort_key(system_id, gated_variant), {})
                .get("behavior_results", 0)
                for system_id in systems
            )
            if pairwise.get("pairs") != expected_pairs:
                violations.append(
                    f"pairwise pairs {pairwise.get('pairs')} does not match expected {expected_pairs}"
                )
            for policy_name, report_name in (
                ("minimum_resolved_fraction", "resolved_fraction"),
                (
                    "minimum_with_skill_win_rate_excluding_ties",
                    "with_skill_win_rate_excluding_ties",
                ),
                ("minimum_raw_reviewer_agreement", "raw_reviewer_agreement"),
            ):
                minimum = pairwise_policy.get(policy_name)
                observed = pairwise.get(report_name)
                if minimum is not None and (observed is None or observed < minimum):
                    violations.append(f"pairwise {report_name} {observed} is below {minimum}")

    for system_id in systems:
        for variant in required_variants:
            cohort = _cohort_key(system_id, variant)
            metadata = report.get("cohorts", {}).get(cohort)
            if not metadata:
                violations.append(f"{cohort}: required cohort is missing")
                continue
            if metadata["replicate_count"] < minimum_replicates:
                violations.append(
                    f"{cohort}: {metadata['replicate_count']} replicates is below {minimum_replicates}"
                )
            for replicate_id in metadata["replicates"]:
                completion = report.get("completion", {}).get(f"{cohort}::{replicate_id}")
                if not completion or not completion["complete"]:
                    violations.append(f"{cohort}::{replicate_id}: incomplete replicate")
            usage = report.get("usage", {}).get(cohort, {})
            if usage.get("identity_complete_results", 0) != usage.get("completed_results", 0):
                violations.append(f"{cohort}: protocol identity metadata is incomplete")
            for field in required_usage_fields:
                metric = usage.get(field, {})
                if metric.get("reported_results", 0) != usage.get("completed_results", 0):
                    violations.append(f"{cohort}: usage field {field} is incomplete")
            implementation = report.get("implementation_metadata", {}).get(cohort, {})
            completed = implementation.get("completed_results", 0)
            for field in required_fields:
                if completed == 0 or implementation.get("field_presence", {}).get(field, 0) != completed:
                    violations.append(f"{cohort}: implementation field {field} is incomplete")
            if isinstance(review_policy, dict):
                minimum_reviews = review_policy.get("minimum_reviews_per_candidate")
                coverage = report.get("review_coverage", {}).get(cohort, {})
                if (
                    isinstance(minimum_reviews, int)
                    and coverage.get("minimum_review_count", 0) < minimum_reviews
                ):
                    violations.append(
                        f"{cohort}: minimum behavior review count "
                        f"{coverage.get('minimum_review_count', 0)} is below {minimum_reviews}"
                    )

        candidate_cohort = _cohort_key(system_id, gated_variant)
        resource_loading = report.get("resource_loading", {}).get(candidate_cohort, {})
        minimum_reporting = efficiency_policy.get("minimum_resource_reporting_rate")
        if minimum_reporting is not None and (
            resource_loading.get("reporting_rate") is None
            or resource_loading["reporting_rate"] < minimum_reporting
        ):
            violations.append(
                f"{candidate_cohort}: resource reporting rate "
                f"{resource_loading.get('reporting_rate')} is below {minimum_reporting}"
            )
        minimum_core = efficiency_policy.get("minimum_core_resource_rate")
        if minimum_core is not None and (
            resource_loading.get("core_complete_rate") is None
            or resource_loading["core_complete_rate"] < minimum_core
        ):
            violations.append(
                f"{candidate_cohort}: core resource rate "
                f"{resource_loading.get('core_complete_rate')} is below {minimum_core}"
            )
        maximum_unknown = efficiency_policy.get("maximum_unknown_resources")
        unknown_count = sum(resource_loading.get("unknown_resources", {}).values())
        if maximum_unknown is not None and unknown_count > maximum_unknown:
            violations.append(
                f"{candidate_cohort}: unknown loaded resources {unknown_count} exceeds {maximum_unknown}"
            )
        maximum_unnecessary = efficiency_policy.get("maximum_unnecessary_resources")
        unnecessary_count = sum(
            resource_loading.get("unnecessary_resources", {}).values()
        )
        if maximum_unnecessary is not None and unnecessary_count > maximum_unnecessary:
            violations.append(
                f"{candidate_cohort}: unnecessary loaded resources {unnecessary_count} "
                f"exceeds {maximum_unnecessary}"
            )
        maximum_overloaded = efficiency_policy.get("maximum_overloaded_profile_results")
        overloaded_results = resource_loading.get("overloaded_profile_results", 0)
        if maximum_overloaded is not None and overloaded_results > maximum_overloaded:
            violations.append(
                f"{candidate_cohort}: overloaded profile results {overloaded_results} "
                f"exceeds {maximum_overloaded}"
            )
        maximum_unexpected = efficiency_policy.get(
            "maximum_unexpected_activation_resource_results"
        )
        unexpected_resources = resource_loading.get(
            "unexpected_activation_resource_results", 0
        )
        if maximum_unexpected is not None and unexpected_resources > maximum_unexpected:
            violations.append(
                f"{candidate_cohort}: unexpected activation resource results "
                f"{unexpected_resources} exceeds {maximum_unexpected}"
            )
        baseline_cohort = _cohort_key(system_id, "previous-skill")
        efficiency_observations: dict[str, Any] = {}
        for metric, maximum_key in (
            ("input_tokens", "maximum_input_token_ratio"),
            ("skill_context_words", "maximum_skill_context_word_ratio"),
            ("turns", "maximum_turn_ratio"),
        ):
            candidate_mean = (
                report.get("usage", {}).get(candidate_cohort, {}).get(metric, {}).get("mean")
            )
            baseline_mean = (
                report.get("usage", {}).get(baseline_cohort, {}).get(metric, {}).get("mean")
            )
            ratio = (
                round(candidate_mean / baseline_mean, 6)
                if isinstance(candidate_mean, (int, float))
                and isinstance(baseline_mean, (int, float))
                and baseline_mean > 0
                else None
            )
            efficiency_observations[metric] = {
                "candidate_mean": candidate_mean,
                "previous_mean": baseline_mean,
                "ratio": ratio,
            }
            maximum = efficiency_policy.get(maximum_key)
            if maximum is not None and (ratio is None or ratio > maximum):
                violations.append(f"{system_id}: {metric} ratio {ratio} exceeds {maximum}")
        activation = report.get("activation", {}).get(candidate_cohort, {})
        for metric in ("precision", "recall", "specificity", "balanced_accuracy", "accuracy"):
            minimum = activation_policy.get(f"minimum_{metric}")
            if minimum is not None and (activation.get(metric) is None or activation[metric] < minimum):
                violations.append(
                    f"{candidate_cohort}: activation {metric} {activation.get(metric)} is below {minimum}"
                )
        maximum_fpr = activation_policy.get("maximum_false_positive_rate")
        if maximum_fpr is not None and (
            activation.get("false_positive_rate") is None
            or activation["false_positive_rate"] > maximum_fpr
        ):
            violations.append(
                f"{candidate_cohort}: false_positive_rate {activation.get('false_positive_rate')} exceeds {maximum_fpr}"
            )
        for slice_name, slice_metrics in report.get("activation_by_slice", {}).get(
            candidate_cohort, {}
        ).items():
            minimum_slice_accuracy = activation_policy.get("minimum_slice_accuracy")
            if minimum_slice_accuracy is not None and (
                slice_metrics.get("accuracy") is None
                or slice_metrics["accuracy"] < minimum_slice_accuracy
            ):
                violations.append(
                    f"{candidate_cohort} {slice_name}: activation accuracy "
                    f"{slice_metrics.get('accuracy')} is below {minimum_slice_accuracy}"
                )
            maximum_slice_fpr = activation_policy.get("maximum_slice_false_positive_rate")
            observed_slice_fpr = slice_metrics.get("false_positive_rate")
            if (
                maximum_slice_fpr is not None
                and observed_slice_fpr is not None
                and observed_slice_fpr > maximum_slice_fpr
            ):
                violations.append(
                    f"{candidate_cohort} {slice_name}: false_positive_rate "
                    f"{observed_slice_fpr} exceeds {maximum_slice_fpr}"
                )
        behavior = report.get("behavior", {}).get(candidate_cohort, {})
        for metric in ("pass_rate", "case_pass_rate"):
            minimum = behavior_policy.get(f"minimum_{metric}")
            if minimum is not None and (behavior.get(metric) is None or behavior[metric] < minimum):
                violations.append(
                    f"{candidate_cohort}: behavior {metric} {behavior.get(metric)} is below {minimum}"
                )
        maximum_ungraded = behavior_policy.get("maximum_ungraded", 0)
        if behavior.get("ungraded", 0) > maximum_ungraded:
            violations.append(f"{candidate_cohort}: ungraded invariants exceed {maximum_ungraded}")
        decision = report.get("decisions", {}).get(candidate_cohort, {})
        minimum_decision_rate = behavior_policy.get("minimum_decision_exact_match_rate")
        if minimum_decision_rate is not None and (
            decision.get("exact_match_rate") is None
            or decision["exact_match_rate"] < minimum_decision_rate
        ):
            violations.append(
                f"{candidate_cohort}: decision exact match {decision.get('exact_match_rate')} is below {minimum_decision_rate}"
            )
        minimum_slice_observations = behavior_policy.get("minimum_slice_observations")
        minimum_slice_pass_rate = behavior_policy.get("minimum_slice_pass_rate")
        if isinstance(minimum_slice_observations, int) and minimum_slice_pass_rate is not None:
            prefix = f"{candidate_cohort}:"
            for slice_key, slice_metrics in report.get("by_tag", {}).items():
                if not slice_key.startswith(prefix):
                    continue
                observations_count = slice_metrics.get("pass", 0) + slice_metrics.get("fail", 0)
                if (
                    observations_count >= minimum_slice_observations
                    and (
                        slice_metrics.get("pass_rate") is None
                        or slice_metrics["pass_rate"] < minimum_slice_pass_rate
                    )
                ):
                    violations.append(
                        f"{slice_key}: behavior pass_rate {slice_metrics.get('pass_rate')} "
                        f"is below {minimum_slice_pass_rate}"
                    )

        paired = report.get("paired_comparisons", {}).get(system_id, {})
        comparisons = {
            metric: paired.get(metric)
            for metric in ("activation_accuracy", "behavior_pass_rate")
        }
        observations[system_id] = {
            "quality": comparisons,
            "efficiency": efficiency_observations,
        }
        for metric, comparison in comparisons.items():
            if comparison is None:
                violations.append(f"{system_id}: comparison {metric} cannot be computed")
                continue
            minimum_delta = comparison_policy.get(f"minimum_{metric}_delta", 0.0)
            if comparison["delta"] < minimum_delta:
                violations.append(
                    f"{system_id}: {metric} delta {comparison['delta']} is below {minimum_delta}"
                )
            minimum_lower_bound = comparison_policy.get(f"minimum_{metric}_lower_bound")
            if (
                minimum_lower_bound is not None
                and comparison["confidence_interval_95"][0] < minimum_lower_bound
            ):
                violations.append(
                    f"{system_id}: {metric} lower bound {comparison['confidence_interval_95'][0]} "
                    f"is below {minimum_lower_bound}"
                )

    gated_behavior_passes = all(
        report.get("behavior", {})
        .get(_cohort_key(system_id, gated_variant), {})
        .get("hard_gate_passed", False)
        for system_id in systems
    )
    evaluated["policy"] = {
        "name": policy.get("name"),
        "version": policy.get("version"),
        "gated_variant": gated_variant,
        "observations": observations,
        "violations": violations,
        "passed": not violations,
    }
    evaluated["hard_gate_passed"] = (
        not evaluated.get("errors") and gated_behavior_passes and not violations
    )
    return evaluated
