"""Shared loading, validation, and scoring primitives."""

from __future__ import annotations

import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable


VALID_GRADES = {"pass", "fail", "not-applicable"}
VALID_VARIANTS = {"with-skill", "without-skill"}
RESULT_FIELDS = {
    "schema_version",
    "protocol_version",
    "run_id",
    "case_id",
    "variant",
    "status",
    "selected_skill",
    "output_text",
    "artifact_path",
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


def validate_case(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    case_id = case.get("id")
    suite = case.get("suite")
    if case.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if not isinstance(case_id, str) or len(case_id) != 3 or case_id[0] not in "TB":
        errors.append("id must match TNN or BNN")
    if suite not in {"activation", "behavior"}:
        errors.append("suite must be activation or behavior")
    if not isinstance(case.get("title"), str) or not case["title"].strip():
        errors.append("title must be non-empty")
    if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
        errors.append("prompt must be non-empty")
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


def validate_result(result: dict[str, Any], cases: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    unknown_fields = set(result) - RESULT_FIELDS
    if unknown_fields:
        errors.append(f"unknown result fields: {', '.join(sorted(unknown_fields))}")
    case_id = result.get("case_id")
    if result.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if "protocol_version" in result and result["protocol_version"] != 1:
        errors.append("protocol_version must be 1 when present")
    if not isinstance(result.get("run_id"), str) or not result["run_id"].strip():
        errors.append("run_id must be non-empty")
    if case_id not in cases:
        errors.append(f"unknown case_id {case_id}")
        return errors
    if result.get("variant") not in VALID_VARIANTS:
        errors.append("variant must be with-skill or without-skill")
    if result.get("status") not in {"completed", "failed", "skipped"}:
        errors.append("status must be completed, failed, or skipped")
    if result.get("selected_skill") is not None and not isinstance(result.get("selected_skill"), bool):
        errors.append("selected_skill must be boolean or null")
    if result.get("output_text") is not None and not isinstance(result.get("output_text"), str):
        errors.append("output_text must be string or null")
    if result.get("artifact_path") is not None and not isinstance(result.get("artifact_path"), str):
        errors.append("artifact_path must be string or null")
    if result.get("grader_notes") is not None and not isinstance(result.get("grader_notes"), str):
        errors.append("grader_notes must be string or null")
    if result.get("error") is not None and not isinstance(result.get("error"), str):
        errors.append("error must be string or null")
    usage = result.get("usage")
    if usage is not None:
        if not isinstance(usage, dict):
            errors.append("usage must be an object")
        else:
            for key in ("input_tokens", "output_tokens", "latency_ms", "cost_usd"):
                value = usage.get(key)
                expected_types = (int,) if key in {"input_tokens", "output_tokens"} else (int, float)
                if value is not None and (
                    isinstance(value, bool) or not isinstance(value, expected_types) or value < 0
                ):
                    expected = "integer" if key in {"input_tokens", "output_tokens"} else "number"
                    errors.append(f"usage.{key} must be a non-negative {expected} or null")
    implementation = result.get("implementation")
    if implementation is not None:
        if not isinstance(implementation, dict):
            errors.append("implementation must be an object")
        elif any(
            not isinstance(key, str)
            or value is not None
            and not isinstance(value, (str, int, float, bool))
            for key, value in implementation.items()
        ):
            errors.append("implementation keys and values must be scalar")
    grades = result.get("invariant_grades", {})
    if not isinstance(grades, dict):
        errors.append("invariant_grades must be an object")
    elif cases[case_id]["suite"] == "behavior":
        valid_ids = {item["id"] for item in cases[case_id]["invariants"]}
        unknown = set(grades) - valid_ids
        if unknown:
            errors.append(f"unknown invariant grades: {', '.join(sorted(unknown))}")
        invalid_values = {value for value in grades.values() if value not in VALID_GRADES}
        if invalid_values:
            errors.append(f"invalid grade values: {', '.join(sorted(invalid_values))}")
    return errors


def load_case_map(paths: Iterable[Path]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for path in paths:
        for case in read_jsonl(path):
            errors = validate_case(case)
            if errors:
                raise EvaluationDataError(f"{path}:{case.get('id', '?')}: {'; '.join(errors)}")
            case_id = case["id"]
            if case_id in cases:
                raise EvaluationDataError(f"duplicate case id {case_id}")
            cases[case_id] = case
    return cases


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def score_results(
    cases: dict[str, dict[str, Any]],
    results: list[dict[str, Any]],
    *,
    require_complete: bool = False,
) -> dict[str, Any]:
    seen: set[tuple[str, str]] = set()
    errors: list[str] = []
    activation_by_variant: dict[str, dict[str, int]] = defaultdict(
        lambda: {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "skipped": 0}
    )
    behavior_by_variant: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "pass": 0,
            "fail": 0,
            "not-applicable": 0,
            "ungraded": 0,
            "critical_failures": 0,
            "critical_ungraded": 0,
        }
    )
    tag_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "fail": 0})
    result_statuses: dict[tuple[str, str], str] = {}
    usage_by_variant: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "completed_results": 0,
            "input_tokens": [],
            "output_tokens": [],
            "latency_ms": [],
            "cost_usd": [],
        }
    )
    implementation_fields: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for result in results:
        result_errors = validate_result(result, cases)
        if result_errors:
            errors.extend(f"{result.get('case_id', '?')}: {error}" for error in result_errors)
            continue
        key = (result["case_id"], result["variant"])
        if key in seen:
            errors.append(f"duplicate result for {key[0]} {key[1]}")
            continue
        seen.add(key)
        result_statuses[key] = result["status"]
        case = cases[result["case_id"]]
        variant = result["variant"]
        if result["status"] != "completed":
            if case["suite"] == "activation":
                activation_by_variant[variant]["skipped"] += 1
            continue
        usage_by_variant[variant]["completed_results"] += 1
        for metric in ("input_tokens", "output_tokens", "latency_ms", "cost_usd"):
            value = (result.get("usage") or {}).get(metric)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                usage_by_variant[variant][metric].append(value)
        for field, value in (result.get("implementation") or {}).items():
            if value is not None and value != "":
                implementation_fields[variant][field] += 1
        if case["suite"] == "activation":
            selected = result.get("selected_skill")
            if not isinstance(selected, bool):
                errors.append(f"{case['id']}: activation result requires selected_skill")
                continue
            expected = case["expected_activation"]
            bucket = "tp" if expected and selected else "tn" if not expected and not selected else "fp" if selected else "fn"
            activation_by_variant[variant][bucket] += 1
            continue

        grades = result.get("invariant_grades", {})
        invariant_by_id = {item["id"]: item for item in case["invariants"]}
        for invariant_id, invariant in invariant_by_id.items():
            grade = grades.get(invariant_id)
            if grade is None:
                behavior_by_variant[variant]["ungraded"] += 1
                if invariant["severity"] == "critical":
                    behavior_by_variant[variant]["critical_ungraded"] += 1
                continue
            behavior_by_variant[variant][grade] += 1
            if grade == "fail" and invariant["severity"] == "critical":
                behavior_by_variant[variant]["critical_failures"] += 1
            if grade in {"pass", "fail"}:
                for tag in case["tags"]:
                    tag_stats[f"{variant}:{tag}"][grade] += 1

    activation_report: dict[str, Any] = {}
    for variant, counts in sorted(activation_by_variant.items()):
        activation_report[variant] = {
            **counts,
            "precision": _safe_ratio(counts["tp"], counts["tp"] + counts["fp"]),
            "recall": _safe_ratio(counts["tp"], counts["tp"] + counts["fn"]),
            "accuracy": _safe_ratio(
                counts["tp"] + counts["tn"],
                counts["tp"] + counts["tn"] + counts["fp"] + counts["fn"],
            ),
        }

    behavior_report: dict[str, Any] = {}
    for variant, counts in sorted(behavior_by_variant.items()):
        graded = counts["pass"] + counts["fail"]
        behavior_report[variant] = {
            **counts,
            "pass_rate": _safe_ratio(counts["pass"], graded),
            "assessment_complete": counts["ungraded"] == 0,
            "hard_gate_passed": counts["critical_failures"] == 0
            and counts["critical_ungraded"] == 0,
        }

    tag_report = {
        key: {**counts, "pass_rate": _safe_ratio(counts["pass"], counts["pass"] + counts["fail"])}
        for key, counts in sorted(tag_stats.items())
    }
    usage_report: dict[str, Any] = {}
    for variant, values in sorted(usage_by_variant.items()):
        usage_report[variant] = {"completed_results": values["completed_results"]}
        for metric in ("input_tokens", "output_tokens", "latency_ms", "cost_usd"):
            samples = values[metric]
            usage_report[variant][metric] = {
                "reported_results": len(samples),
                "total": round(sum(samples), 6) if samples else None,
                "mean": round(sum(samples) / len(samples), 6) if samples else None,
            }
    implementation_report = {
        variant: {
            "completed_results": usage_report.get(variant, {}).get("completed_results", 0),
            "field_presence": dict(sorted(implementation_fields[variant].items())),
        }
        for variant in sorted(set(usage_report) | set(implementation_fields))
    }
    variants = sorted(
        {
            result.get("variant")
            for result in results
            if result.get("variant") in VALID_VARIANTS
        }
    )
    completion_report: dict[str, Any] = {}
    if require_complete and not variants:
        errors.append("complete scoring requires at least one valid result variant")
    for variant in variants:
        completed_ids = sorted(
            case_id
            for case_id in cases
            if result_statuses.get((case_id, variant)) == "completed"
        )
        incomplete_ids = sorted(set(cases) - set(completed_ids))
        completion_report[variant] = {
            "expected_cases": len(cases),
            "completed_cases": len(completed_ids),
            "incomplete_case_ids": incomplete_ids,
            "complete": not incomplete_ids,
        }
        if require_complete and incomplete_ids:
            errors.append(
                f"{variant}: {len(incomplete_ids)} required cases are missing, failed, or skipped"
            )

    return {
        "schema_version": "1.0",
        "require_complete": require_complete,
        "errors": errors,
        "completion": completion_report,
        "activation": activation_report,
        "behavior": behavior_report,
        "by_tag": tag_report,
        "usage": usage_report,
        "implementation_metadata": implementation_report,
        "hard_gate_passed": not errors
        and all(report["hard_gate_passed"] for report in behavior_report.values()),
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
    if policy.get("schema_version") != "1.0":
        violations.append("release policy schema_version must be 1.0")
    if not isinstance(policy.get("name"), str) or not policy["name"].strip():
        violations.append("release policy name must be non-empty")
    if not isinstance(policy.get("version"), str) or not policy["version"].strip():
        violations.append("release policy version must be non-empty")
    required_variants = policy.get("required_variants", [])
    if not isinstance(required_variants, list) or any(
        variant not in VALID_VARIANTS for variant in required_variants
    ):
        violations.append("release policy required_variants are invalid")
        required_variants = []
    for variant in required_variants:
        completion = evaluated.get("completion", {}).get(variant)
        if not completion or not completion.get("complete"):
            violations.append(f"{variant}: required variant is incomplete")

    gated_variant = policy.get("gated_variant")
    if gated_variant not in VALID_VARIANTS:
        violations.append("release policy gated_variant is invalid")
    else:
        activation = evaluated.get("activation", {}).get(gated_variant, {})
        activation_minimums = policy.get("activation_minimums", {})
        if not isinstance(activation_minimums, dict):
            violations.append("release policy activation_minimums must be an object")
            activation_minimums = {}
        for metric, minimum in activation_minimums.items():
            actual = activation.get(metric)
            if isinstance(minimum, bool) or not isinstance(minimum, (int, float)) or not 0 <= minimum <= 1:
                violations.append(f"activation minimum {metric} is invalid")
            elif actual is None or actual < minimum:
                violations.append(f"{gated_variant}: activation {metric} {actual} is below {minimum}")
        behavior = evaluated.get("behavior", {}).get(gated_variant, {})
        behavior_policy = policy.get("behavior", {})
        if not isinstance(behavior_policy, dict):
            violations.append("release policy behavior must be an object")
            behavior_policy = {}
        minimum_pass_rate = behavior_policy.get("minimum_pass_rate")
        if minimum_pass_rate is not None and (
            isinstance(minimum_pass_rate, bool)
            or not isinstance(minimum_pass_rate, (int, float))
            or not 0 <= minimum_pass_rate <= 1
        ):
            violations.append("behavior minimum_pass_rate is invalid")
        elif isinstance(minimum_pass_rate, (int, float)):
            actual_pass_rate = behavior.get("pass_rate")
            if actual_pass_rate is None or actual_pass_rate < minimum_pass_rate:
                violations.append(
                    f"{gated_variant}: behavior pass_rate {actual_pass_rate} is below {minimum_pass_rate}"
                )
        maximum_ungraded = behavior_policy.get("maximum_ungraded")
        if maximum_ungraded is not None and (
            isinstance(maximum_ungraded, bool)
            or not isinstance(maximum_ungraded, int)
            or maximum_ungraded < 0
        ):
            violations.append("behavior maximum_ungraded is invalid")
        elif isinstance(maximum_ungraded, int) and behavior.get("ungraded", 0) > maximum_ungraded:
            violations.append(
                f"{gated_variant}: behavior ungraded {behavior.get('ungraded')} exceeds {maximum_ungraded}"
            )
        required_fields = policy.get("required_implementation_fields", [])
        if not isinstance(required_fields, list) or any(
            not isinstance(field, str) or not field for field in required_fields
        ):
            violations.append("required_implementation_fields must be a string array")
            required_fields = []
        for metadata_variant in required_variants:
            metadata = evaluated.get("implementation_metadata", {}).get(metadata_variant, {})
            completed_results = metadata.get("completed_results", 0)
            field_presence = metadata.get("field_presence", {})
            for field in required_fields:
                if field_presence.get(field, 0) != completed_results or completed_results == 0:
                    violations.append(
                        f"{metadata_variant}: implementation field {field} is incomplete"
                    )

    comparison = policy.get("comparison", {})
    if not isinstance(comparison, dict):
        violations.append("release policy comparison must be an object")
        comparison = {}
    baseline_variant = comparison.get("baseline_variant")
    if gated_variant in VALID_VARIANTS and baseline_variant in VALID_VARIANTS:
        metric_sources = {
            "activation_accuracy_delta": ("activation", "accuracy"),
            "behavior_pass_rate_delta": ("behavior", "pass_rate"),
        }
        for policy_metric, (section, metric) in metric_sources.items():
            minimum_delta = comparison.get(f"minimum_{policy_metric}")
            if minimum_delta is None:
                continue
            if isinstance(minimum_delta, bool) or not isinstance(minimum_delta, (int, float)):
                violations.append(f"comparison minimum_{policy_metric} is invalid")
                continue
            candidate_value = evaluated.get(section, {}).get(gated_variant, {}).get(metric)
            baseline_value = evaluated.get(section, {}).get(baseline_variant, {}).get(metric)
            if candidate_value is None or baseline_value is None:
                violations.append(f"comparison {policy_metric} cannot be computed")
                continue
            delta = round(candidate_value - baseline_value, 6)
            observations[policy_metric] = delta
            if delta < minimum_delta:
                violations.append(f"comparison {policy_metric} {delta} is below {minimum_delta}")

    evaluated["policy"] = {
        "name": policy.get("name"),
        "version": policy.get("version"),
        "gated_variant": gated_variant,
        "observations": observations,
        "violations": violations,
        "passed": not violations,
    }
    gated_behavior = evaluated.get("behavior", {}).get(gated_variant, {})
    evaluated["hard_gate_passed"] = (
        not evaluated.get("errors")
        and gated_behavior.get("hard_gate_passed", False)
        and not violations
    )
    return evaluated
