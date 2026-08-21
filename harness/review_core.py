"""Blinded review packet preparation and conservative grade aggregation."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

from harness.eval_core import VALID_GRADES, VALID_VARIANTS, validate_result


class ReviewDataError(ValueError):
    """Raised when review data cannot be safely matched or aggregated."""


def prepare_review_packet(
    cases: dict[str, dict[str, Any]],
    results: list[dict[str, Any]],
    salt: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not salt:
        raise ReviewDataError("review salt must be non-empty")
    packets: list[dict[str, Any]] = []
    keys: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for result in results:
        errors = validate_result(result, cases)
        if errors:
            raise ReviewDataError(f"{result.get('case_id', '?')}: {'; '.join(errors)}")
        case = cases[result["case_id"]]
        if case["suite"] != "behavior" or result["status"] != "completed":
            continue
        if not isinstance(result.get("output_text"), str) or not result["output_text"].strip():
            raise ReviewDataError(
                f"{result['case_id']}: completed behavior result requires reviewable output_text"
            )
        result_key = (result["case_id"], result["variant"])
        if result_key in seen:
            raise ReviewDataError(f"duplicate candidate result for {result_key}")
        seen.add(result_key)
        digest_input = "\0".join(
            (salt, result["run_id"], result["case_id"], result["variant"])
        ).encode("utf-8")
        review_id = "R-" + hashlib.sha256(digest_input).hexdigest()[:20]
        packets.append(
            {
                "schema_version": "1.0",
                "review_id": review_id,
                "case": {
                    "id": case["id"],
                    "title": case["title"],
                    "prompt": case["prompt"],
                    "tags": case["tags"],
                    "invariants": case["invariants"],
                },
                "candidate": {"output_text": result.get("output_text")},
                "instructions": {
                    "allowed_grades": sorted(VALID_GRADES),
                    "grade_each_invariant_independently": True,
                    "cite_observable_evidence": True,
                    "do_not_infer_candidate_identity": True,
                },
            }
        )
        keys.append(
            {
                "schema_version": "1.0",
                "review_id": review_id,
                "run_id": result["run_id"],
                "case_id": result["case_id"],
                "variant": result["variant"],
            }
        )
    return packets, keys


def _validate_review(
    review: dict[str, Any],
    key_by_review_id: dict[str, dict[str, Any]],
    cases: dict[str, dict[str, Any]],
) -> None:
    if review.get("schema_version") != "1.0":
        raise ReviewDataError("review schema_version must be 1.0")
    review_id = review.get("review_id")
    if review_id not in key_by_review_id:
        raise ReviewDataError(f"unknown review_id {review_id}")
    if not isinstance(review.get("reviewer_id"), str) or not review["reviewer_id"].strip():
        raise ReviewDataError(f"{review_id}: reviewer_id must be non-empty")
    if review.get("reviewer_kind") not in {"automated", "human", "model"}:
        raise ReviewDataError(f"{review_id}: invalid reviewer_kind")
    grades = review.get("grades")
    if not isinstance(grades, dict):
        raise ReviewDataError(f"{review_id}: grades must be an object")
    case = cases[key_by_review_id[review_id]["case_id"]]
    invariant_ids = {invariant["id"] for invariant in case["invariants"]}
    unknown_ids = set(grades) - invariant_ids
    if unknown_ids:
        raise ReviewDataError(f"{review_id}: unknown invariant IDs {sorted(unknown_ids)}")
    invalid_grades = {grade for grade in grades.values() if grade not in VALID_GRADES}
    if invalid_grades:
        raise ReviewDataError(f"{review_id}: invalid grades {sorted(invalid_grades)}")


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
    pass_count = grades.count("pass")
    fail_count = grades.count("fail")
    if pass_count > fail_count:
        return "pass"
    if fail_count > pass_count:
        return "fail"
    if pass_count == fail_count == 0:
        return "not-applicable"
    return None


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
    result_key_by_review_id: dict[str, tuple[str, str, str]] = {}
    for key in review_keys:
        review_id = key.get("review_id")
        if not isinstance(review_id, str) or review_id in key_by_review_id:
            raise ReviewDataError(f"invalid or duplicate review key {review_id}")
        case_id = key.get("case_id")
        if case_id not in cases or cases[case_id]["suite"] != "behavior":
            raise ReviewDataError(f"{review_id}: key references an unknown behavior case")
        result_key = (key.get("run_id"), case_id, key.get("variant"))
        if not all(isinstance(value, str) and value for value in result_key):
            raise ReviewDataError(f"{review_id}: incomplete review key")
        if key.get("variant") not in VALID_VARIANTS:
            raise ReviewDataError(f"{review_id}: invalid result variant")
        key_by_review_id[review_id] = key
        result_key_by_review_id[review_id] = result_key

    reviews_by_result: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
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
        result_key = (result["run_id"], result["case_id"], result["variant"])
        candidate_reviews = reviews_by_result.get(result_key, [])
        consensus: dict[str, str] = {}
        unresolved: list[str] = []
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
        else:
            unresolved.extend(invariant["id"] for invariant in case["invariants"])
        result["invariant_grades"] = consensus
        notes = f"independent reviews: {len(candidate_reviews)}"
        if unresolved:
            notes += f"; unresolved: {', '.join(unresolved)}"
        result["grader_notes"] = notes
        implementation = dict(result.get("implementation") or {})
        implementation.update(
            {
                "review_count": len(candidate_reviews),
                "review_policy": "critical-any-fail; noncritical-majority",
            }
        )
        result["implementation"] = implementation
        merged.append(result)
    return merged
