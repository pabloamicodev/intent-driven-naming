"""Blinded artifact review, conservative consensus, and reviewer agreement."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from harness.eval_core import VALID_DECISIONS, VALID_GRADES, VALID_VARIANTS, validate_result


class ReviewDataError(ValueError):
    """Raised when review data cannot be safely matched or aggregated."""


def _result_key(record: dict[str, Any]) -> tuple[str, str, str, str, str, int]:
    return (
        record["run_id"],
        record.get("system_id", "legacy"),
        record["variant"],
        record.get("replicate_id", "r1"),
        record["case_id"],
        record.get("attempt", 1),
    )


def _load_artifact(result: dict[str, Any], artifact_root: Path | None) -> dict[str, Any] | None:
    bundle = result.get("artifact_bundle")
    if not bundle or bundle.get("format") == "none":
        return None
    relative_path = bundle.get("path")
    if not isinstance(relative_path, str) or not relative_path:
        raise ReviewDataError(f"{result['case_id']}: artifact bundle path is missing")
    if artifact_root is None:
        raise ReviewDataError("artifact_root is required when results reference artifacts")
    root = artifact_root.resolve()
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ReviewDataError(f"{result['case_id']}: artifact path escapes artifact_root") from exc
    if not path.is_file():
        raise ReviewDataError(f"{result['case_id']}: artifact bundle does not exist: {relative_path}")
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if bundle.get("sha256") and bundle["sha256"] != digest:
        raise ReviewDataError(f"{result['case_id']}: artifact bundle hash mismatch")
    try:
        artifact = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ReviewDataError(f"{result['case_id']}: artifact bundle is not valid JSON") from exc
    if not isinstance(artifact, dict):
        raise ReviewDataError(f"{result['case_id']}: artifact bundle must be a JSON object")
    return artifact


def prepare_review_packet(
    cases: dict[str, dict[str, Any]],
    results: list[dict[str, Any]],
    salt: str,
    *,
    artifact_root: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not salt:
        raise ReviewDataError("review salt must be non-empty")
    packets: list[dict[str, Any]] = []
    keys: list[dict[str, Any]] = []
    selected: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for result in results:
        errors = validate_result(result, cases)
        if errors:
            raise ReviewDataError(f"{result.get('case_id', '?')}: {'; '.join(errors)}")
        case = cases[result["case_id"]]
        if case["suite"] != "behavior" or result["status"] != "completed":
            continue
        key_tuple = _result_key(result)
        base_key = key_tuple[:-1]
        previous = selected.get(base_key)
        if previous and previous.get("attempt", 1) == result.get("attempt", 1):
            raise ReviewDataError(f"duplicate candidate result for {key_tuple}")
        if previous is None or result.get("attempt", 1) > previous.get("attempt", 1):
            selected[base_key] = result
    for _, result in sorted(selected.items()):
        case = cases[result["case_id"]]
        artifact = _load_artifact(result, artifact_root)
        output_text = result.get("output_text")
        if (not isinstance(output_text, str) or not output_text.strip()) and artifact is None:
            raise ReviewDataError(
                f"{result['case_id']}: completed behavior result requires output_text or artifact bundle"
            )
        key_tuple = _result_key(result)
        digest_input = "\0".join((salt, *(str(value) for value in key_tuple))).encode("utf-8")
        review_id = "R-" + hashlib.sha256(digest_input).hexdigest()[:20]
        packets.append(
            {
                "schema_version": "1.1",
                "review_id": review_id,
                "case": {
                    "id": case["id"],
                    "title": case["title"],
                    "prompt": case["prompt"],
                    "mode": case["mode"],
                    "languages": case["languages"],
                    "contract_risk": case["contract_risk"],
                    "invariants": case["invariants"],
                },
                "candidate": {"output_text": output_text, "artifact": artifact},
                "instructions": {
                    "allowed_grades": sorted(VALID_GRADES),
                    "allowed_decisions": sorted(VALID_DECISIONS),
                    "grade_each_invariant_independently": True,
                    "cite_observable_evidence_for_every_grade": True,
                    "record_observed_decisions_without_seeing_expected_labels": True,
                    "do_not_infer_candidate_identity": True,
                },
            }
        )
        keys.append(
            {
                "schema_version": "1.1",
                "review_id": review_id,
                "run_id": key_tuple[0],
                "system_id": key_tuple[1],
                "variant": key_tuple[2],
                "replicate_id": key_tuple[3],
                "case_id": key_tuple[4],
                "attempt": key_tuple[5],
            }
        )
    return packets, keys


def _validate_review(
    review: dict[str, Any],
    key_by_review_id: dict[str, dict[str, Any]],
    cases: dict[str, dict[str, Any]],
) -> None:
    if review.get("schema_version") != "1.1":
        raise ReviewDataError("review schema_version must be 1.1")
    review_id = review.get("review_id")
    if review_id not in key_by_review_id:
        raise ReviewDataError(f"unknown review_id {review_id}")
    if not isinstance(review.get("reviewer_id"), str) or not review["reviewer_id"].strip():
        raise ReviewDataError(f"{review_id}: reviewer_id must be non-empty")
    if review.get("reviewer_kind") not in {"automated", "human", "model"}:
        raise ReviewDataError(f"{review_id}: invalid reviewer_kind")
    grades = review.get("grades")
    evidence = review.get("evidence")
    if not isinstance(grades, dict) or not isinstance(evidence, dict):
        raise ReviewDataError(f"{review_id}: grades and evidence must be objects")
    case = cases[key_by_review_id[review_id]["case_id"]]
    invariant_ids = {invariant["id"] for invariant in case["invariants"]}
    unknown_ids = set(grades) - invariant_ids
    if unknown_ids:
        raise ReviewDataError(f"{review_id}: unknown invariant IDs {sorted(unknown_ids)}")
    invalid_grades = {grade for grade in grades.values() if grade not in VALID_GRADES}
    if invalid_grades:
        raise ReviewDataError(f"{review_id}: invalid grades {sorted(invalid_grades)}")
    missing_evidence = {
        invariant_id
        for invariant_id in grades
        if not isinstance(evidence.get(invariant_id), str) or not evidence[invariant_id].strip()
    }
    if missing_evidence:
        raise ReviewDataError(f"{review_id}: missing evidence for {sorted(missing_evidence)}")
    decisions = review.get("observed_decisions")
    if not isinstance(decisions, list) or not decisions or any(
        decision not in VALID_DECISIONS for decision in decisions
    ):
        raise ReviewDataError(f"{review_id}: observed_decisions are invalid")
    if len(decisions) != len(set(decisions)):
        raise ReviewDataError(f"{review_id}: observed_decisions must be unique")


def _consensus_grade(severity: str, grades: list[str]) -> str | None:
    if not grades:
        return None
    if severity == "critical":
        if "fail" in grades:
            return "fail"
        if all(grade == "pass" for grade in grades):
            return "pass"
        if all(grade == "not-applicable" for grade in grades):
            return "not-applicable"
        return None
    counts = Counter(grades)
    winner, winner_count = counts.most_common(1)[0]
    return winner if winner_count > len(grades) / 2 else None


def review_agreement(
    cases: dict[str, dict[str, Any]],
    review_keys: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    key_by_review_id = {key["review_id"]: key for key in review_keys}
    for review in reviews:
        _validate_review(review, key_by_review_id, cases)
    by_review_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for review in reviews:
        by_review_id[review["review_id"]].append(review)
    agreement_pairs = 0
    grade_agreements = 0
    category_counts: Counter[str] = Counter()
    decision_pairs = 0
    decision_agreements = 0
    disagreement_records: list[dict[str, str]] = []
    for review_id, candidate_reviews in by_review_id.items():
        for left, right in combinations(candidate_reviews, 2):
            shared = sorted(set(left["grades"]) & set(right["grades"]))
            for invariant_id in shared:
                left_grade = left["grades"][invariant_id]
                right_grade = right["grades"][invariant_id]
                agreement_pairs += 1
                grade_agreements += int(left_grade == right_grade)
                category_counts.update((left_grade, right_grade))
                if left_grade != right_grade:
                    disagreement_records.append(
                        {
                            "review_id": review_id,
                            "item": invariant_id,
                            "left": left_grade,
                            "right": right_grade,
                        }
                    )
            decision_pairs += 1
            left_decisions = sorted(left["observed_decisions"])
            right_decisions = sorted(right["observed_decisions"])
            decision_agreements += int(left_decisions == right_decisions)
    raw_agreement = grade_agreements / agreement_pairs if agreement_pairs else None
    total_ratings = sum(category_counts.values())
    expected_agreement = (
        sum((count / total_ratings) ** 2 for count in category_counts.values())
        if total_ratings
        else None
    )
    if raw_agreement == 1 and expected_agreement == 1:
        kappa = 1.0
    elif raw_agreement is not None and expected_agreement is not None and expected_agreement < 1:
        kappa = (raw_agreement - expected_agreement) / (1 - expected_agreement)
    else:
        kappa = None
    return {
        "schema_version": "1.0",
        "reviewed_candidates": len(by_review_id),
        "review_records": len(reviews),
        "minimum_reviews_per_candidate": min(
            (len(candidate_reviews) for candidate_reviews in by_review_id.values()),
            default=0,
        ),
        "grade_pairs": agreement_pairs,
        "raw_grade_agreement": round(raw_agreement, 6) if raw_agreement is not None else None,
        "chance_corrected_grade_agreement": round(kappa, 6) if kappa is not None else None,
        "decision_set_agreement": round(decision_agreements / decision_pairs, 6)
        if decision_pairs
        else None,
        "disagreements": disagreement_records,
    }


def merge_reviews(
    cases: dict[str, dict[str, Any]],
    results: list[dict[str, Any]],
    review_keys: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    *,
    minimum_reviews: int = 1,
) -> list[dict[str, Any]]:
    if minimum_reviews < 1:
        raise ReviewDataError("minimum_reviews must be at least 1")
    key_by_review_id: dict[str, dict[str, Any]] = {}
    result_key_by_review_id: dict[str, tuple[str, str, str, str, str, int]] = {}
    for key in review_keys:
        review_id = key.get("review_id")
        if not isinstance(review_id, str) or review_id in key_by_review_id:
            raise ReviewDataError(f"invalid or duplicate review key {review_id}")
        case_id = key.get("case_id")
        if case_id not in cases or cases[case_id]["suite"] != "behavior":
            raise ReviewDataError(f"{review_id}: key references an unknown behavior case")
        if key.get("variant") not in VALID_VARIANTS:
            raise ReviewDataError(f"{review_id}: invalid result variant")
        result_key = (
            key.get("run_id"),
            key.get("system_id", "legacy"),
            key.get("variant"),
            key.get("replicate_id", "r1"),
            case_id,
            key.get("attempt", 1),
        )
        if not all(isinstance(value, str) and value for value in result_key[:-1]) or not isinstance(
            result_key[-1], int
        ):
            raise ReviewDataError(f"{review_id}: incomplete review key")
        key_by_review_id[review_id] = key
        result_key_by_review_id[review_id] = result_key

    reviews_by_result: dict[tuple[str, str, str, str, str, int], list[dict[str, Any]]] = defaultdict(list)
    reviewers_seen: set[tuple[str, str]] = set()
    for review in reviews:
        _validate_review(review, key_by_review_id, cases)
        unique_reviewer = (review["review_id"], review["reviewer_id"])
        if unique_reviewer in reviewers_seen:
            raise ReviewDataError(f"duplicate review from {review['reviewer_id']} for {review['review_id']}")
        reviewers_seen.add(unique_reviewer)
        reviews_by_result[result_key_by_review_id[review["review_id"]]].append(review)

    merged: list[dict[str, Any]] = []
    for original in results:
        result = dict(original)
        case = cases.get(result.get("case_id"))
        if not case or case["suite"] != "behavior" or result.get("status") != "completed":
            merged.append(result)
            continue
        candidate_reviews = reviews_by_result.get(_result_key(result), [])
        consensus: dict[str, str] = {}
        unresolved: list[str] = []
        decision_consensus: list[str] = []
        if len(candidate_reviews) >= minimum_reviews:
            for invariant in case["invariants"]:
                invariant_id = invariant["id"]
                grades = [
                    review["grades"][invariant_id]
                    for review in candidate_reviews
                    if invariant_id in review["grades"]
                ]
                grade = _consensus_grade(invariant["severity"], grades)
                if grade is None:
                    unresolved.append(invariant_id)
                else:
                    consensus[invariant_id] = grade
            decision_counts = Counter(
                decision
                for review in candidate_reviews
                for decision in review["observed_decisions"]
            )
            decision_consensus = sorted(
                decision
                for decision, count in decision_counts.items()
                if count > len(candidate_reviews) / 2
            )
        else:
            unresolved.extend(invariant["id"] for invariant in case["invariants"])
        result["invariant_grades"] = consensus
        if decision_consensus:
            result["observed_decisions"] = decision_consensus
        else:
            result.pop("observed_decisions", None)
        notes = f"independent reviews: {len(candidate_reviews)}"
        if unresolved:
            notes += f"; unresolved: {', '.join(unresolved)}"
        if not decision_consensus:
            notes += "; unresolved decisions"
        result["grader_notes"] = notes
        implementation = dict(result.get("implementation") or {})
        implementation.update(
            {
                "review_count": len(candidate_reviews),
                "review_policy": "critical-any-fail; noncritical-majority; decision-majority",
            }
        )
        result["implementation"] = implementation
        merged.append(result)
    return merged
