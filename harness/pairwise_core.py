"""Blinded pairwise comparison of with-skill and without-skill outputs."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from harness.eval_core import validate_result
from harness.review_core import ReviewDataError, _load_artifact

VALID_PREFERENCES = {"A", "B", "tie"}


def _review_candidate(
    variants: dict[str, dict[str, Any]],
    artifact_root: Path | None,
    pair_id: str,
    label: str,
    variant: str,
) -> dict[str, Any]:
    result = variants[variant]
    artifact = _load_artifact(result, artifact_root)
    output_text = result.get("output_text")
    if (not isinstance(output_text, str) or not output_text.strip()) and artifact is None:
        raise ReviewDataError(f"{pair_id}: candidate {label} has no reviewable output")
    return {"label": label, "output_text": output_text, "artifact": artifact}


def prepare_pairwise_packet(
    cases: dict[str, dict[str, Any]],
    results: list[dict[str, Any]],
    salt: str,
    *,
    artifact_root=None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not salt:
        raise ReviewDataError("pairwise salt must be non-empty")
    grouped: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for result in results:
        errors = validate_result(result, cases)
        if errors:
            raise ReviewDataError(f"{result.get('case_id', '?')}: {'; '.join(errors)}")
        case = cases[result["case_id"]]
        if case["suite"] != "behavior" or result["status"] != "completed":
            continue
        group = (
            result.get("system_id", "legacy"),
            result.get("replicate_id", "r1"),
            result["case_id"],
        )
        variant = result["variant"]
        previous = grouped[group].get(variant)
        if previous and previous.get("attempt", 1) == result.get("attempt", 1):
            raise ReviewDataError(f"duplicate pairwise candidate for {group} {variant}")
        if previous is None or result.get("attempt", 1) > previous.get("attempt", 1):
            grouped[group][variant] = result

    packets: list[dict[str, Any]] = []
    keys: list[dict[str, Any]] = []
    for group, variants in sorted(grouped.items()):
        if set(variants) != {"with-skill", "without-skill"}:
            continue
        configuration_hashes = {result["configuration_hash"] for result in variants.values()}
        if len(configuration_hashes) != 1:
            raise ReviewDataError(f"{group}: pairwise candidates use different configurations")
        digest = hashlib.sha256("\0".join((salt, *group)).encode("utf-8")).hexdigest()
        pair_id = "P-" + digest[:20]
        orientation = (
            ("with-skill", "without-skill")
            if int(digest[20], 16) % 2 == 0
            else ("without-skill", "with-skill")
        )

        case = cases[group[2]]
        packets.append(
            {
                "schema_version": "1.0",
                "pair_id": pair_id,
                "case": {
                    "title": case["title"],
                    "prompt": case["prompt"],
                    "mode": case["mode"],
                    "languages": case["languages"],
                    "contract_risk": case["contract_risk"],
                    "invariants": case["invariants"],
                },
                "candidates": [
                    _review_candidate(variants, artifact_root, pair_id, "A", orientation[0]),
                    _review_candidate(variants, artifact_root, pair_id, "B", orientation[1]),
                ],
                "instructions": {
                    "preference": ["A", "B", "tie"],
                    "judge_correctness_and_contract_safety_before_style": True,
                    "cite_observable_evidence": True,
                    "do_not_infer_candidate_identity": True,
                },
            }
        )
        keys.append(
            {
                "schema_version": "1.0",
                "pair_id": pair_id,
                "system_id": group[0],
                "replicate_id": group[1],
                "case_id": group[2],
                "A_variant": orientation[0],
                "B_variant": orientation[1],
            }
        )
    return packets, keys


def score_pairwise(
    keys: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    *,
    minimum_reviews: int = 2,
) -> dict[str, Any]:
    if minimum_reviews < 1:
        raise ReviewDataError("minimum_reviews must be positive")
    key_map = {key.get("pair_id"): key for key in keys}
    if None in key_map or len(key_map) != len(keys):
        raise ReviewDataError("pairwise keys contain missing or duplicate pair IDs")
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for review in reviews:
        if review.get("schema_version") != "1.1":
            raise ReviewDataError("pairwise review schema_version must be 1.1")
        pair_id = review.get("pair_id")
        reviewer_id = review.get("reviewer_id")
        if pair_id not in key_map:
            raise ReviewDataError(f"unknown pair_id {pair_id}")
        if not isinstance(reviewer_id, str) or not reviewer_id.strip():
            raise ReviewDataError(f"{pair_id}: reviewer_id must be non-empty")
        if review.get("reviewer_kind") not in {"human", "model", "automated"}:
            raise ReviewDataError(f"{pair_id}: reviewer_kind is invalid")
        if review.get("preference") not in VALID_PREFERENCES:
            raise ReviewDataError(f"{pair_id}: invalid preference")
        if not isinstance(review.get("evidence"), str) or not review["evidence"].strip():
            raise ReviewDataError(f"{pair_id}: evidence must be non-empty")
        if (pair_id, reviewer_id) in seen:
            raise ReviewDataError(f"{pair_id}: duplicate reviewer {reviewer_id}")
        seen.add((pair_id, reviewer_id))
        by_pair[pair_id].append(review)

    totals = Counter({"with-skill": 0, "without-skill": 0, "tie": 0, "unresolved": 0})
    pair_results: list[dict[str, Any]] = []
    human_reviews = [review for review in reviews if review["reviewer_kind"] == "human"]
    agreement_population = "human" if human_reviews else "all-reviewers"
    agreement_pairs = 0
    agreement_count = 0
    for pair_id, key in sorted(key_map.items()):
        candidate_reviews = by_pair.get(pair_id, [])
        human_candidate_reviews = [
            review for review in candidate_reviews if review["reviewer_kind"] == "human"
        ]
        consensus_reviews = human_candidate_reviews or candidate_reviews
        agreement_reviews = (
            human_candidate_reviews if agreement_population == "human" else candidate_reviews
        )
        for left_index, left in enumerate(agreement_reviews):
            for right in agreement_reviews[left_index + 1 :]:
                agreement_pairs += 1
                agreement_count += int(left["preference"] == right["preference"])
        counts = Counter(review["preference"] for review in consensus_reviews)
        consensus = "unresolved"
        if len(consensus_reviews) >= minimum_reviews and counts:
            label, count = counts.most_common(1)[0]
            if count > len(consensus_reviews) / 2:
                consensus = label if label == "tie" else key[f"{label}_variant"]
        totals[consensus] += 1
        pair_results.append(
            {
                "pair_id": pair_id,
                "case_id": key["case_id"],
                "system_id": key["system_id"],
                "replicate_id": key["replicate_id"],
                "review_count": len(candidate_reviews),
                "human_review_count": sum(
                    review["reviewer_kind"] == "human" for review in candidate_reviews
                ),
                "consensus": consensus,
            }
        )
    resolved = totals["with-skill"] + totals["without-skill"] + totals["tie"]
    return {
        "schema_version": "1.1",
        "pairs": len(keys),
        "review_records": len(reviews),
        "human_review_records": sum(review["reviewer_kind"] == "human" for review in reviews),
        "agreement_population": agreement_population,
        "minimum_human_reviews_per_pair": min(
            (
                sum(review["reviewer_kind"] == "human" for review in by_pair.get(pair_id, []))
                for pair_id in key_map
            ),
            default=0,
        ),
        "resolved_pairs": resolved,
        "resolved_fraction": round(resolved / len(keys), 6) if keys else None,
        "with_skill_wins": totals["with-skill"],
        "without_skill_wins": totals["without-skill"],
        "ties": totals["tie"],
        "unresolved": totals["unresolved"],
        "with_skill_win_rate_excluding_ties": round(
            totals["with-skill"] / (totals["with-skill"] + totals["without-skill"]), 6
        )
        if totals["with-skill"] + totals["without-skill"]
        else None,
        "raw_reviewer_agreement": round(agreement_count / agreement_pairs, 6)
        if agreement_pairs
        else None,
        "pair_results": pair_results,
    }
