#!/usr/bin/env python3
"""Resolve blinded A/B reviews and report with-skill win rates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import pairwise_core
from harness.eval_core import read_jsonl
from harness.review_core import ReviewDataError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keys", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, required=True)
    parser.add_argument("--minimum-reviews", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = pairwise_core.score_pairwise(
            read_jsonl(args.keys),
            read_jsonl(args.reviews),
            minimum_reviews=args.minimum_reviews,
        )
    except ReviewDataError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"scored {report['resolved_pairs']}/{report['pairs']} pairs; "
        f"with-skill wins={report['with_skill_wins']}"
    )
    return 0 if report["unresolved"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
