#!/usr/bin/env python3
"""Merge independent invariant reviews into raw candidate results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.eval_core import EvaluationDataError, load_case_map, read_jsonl, write_jsonl
from harness.review_core import ReviewDataError, merge_reviews, review_agreement

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, nargs="+", required=True)
    parser.add_argument("--review-keys", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--agreement-output", type=Path)
    parser.add_argument("--behavior-cases", type=Path, default=ROOT / "evals/cases/behavior.jsonl")
    parser.add_argument("--minimum-reviews", type=int, default=1)
    args = parser.parse_args()

    try:
        cases = load_case_map([args.behavior_cases])
        results = [record for path in args.results for record in read_jsonl(path)]
        keys = read_jsonl(args.review_keys)
        reviews = [record for path in args.reviews for record in read_jsonl(path)]
        merged = merge_reviews(
            cases,
            results,
            keys,
            reviews,
            minimum_reviews=args.minimum_reviews,
        )
        agreement = review_agreement(cases, keys, reviews)
    except (EvaluationDataError, ReviewDataError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    write_jsonl(args.output, merged)
    if args.agreement_output:
        args.agreement_output.parent.mkdir(parents=True, exist_ok=True)
        args.agreement_output.write_text(
            json.dumps(agreement, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(f"wrote {len(merged)} graded results to {args.output}")
    print(
        "review agreement: "
        f"raw={agreement['raw_grade_agreement']} "
        f"chance-corrected={agreement['chance_corrected_grade_agreement']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
