#!/usr/bin/env python3
"""Create blinded A/B review packets from paired evaluation results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.eval_core import EvaluationDataError, load_case_map, read_jsonl, write_jsonl
from harness.pairwise_core import prepare_pairwise_packet
from harness.review_core import ReviewDataError


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, nargs="+", required=True)
    parser.add_argument("--behavior-cases", type=Path, default=ROOT / "evals/cases/behavior.jsonl")
    parser.add_argument("--salt", required=True)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--packet-output", type=Path, required=True)
    parser.add_argument("--key-output", type=Path, required=True)
    args = parser.parse_args()
    try:
        cases = load_case_map([args.behavior_cases])
        results = [record for path in args.results for record in read_jsonl(path)]
        packets, keys = prepare_pairwise_packet(
            cases, results, args.salt, artifact_root=args.artifact_root
        )
    except (EvaluationDataError, ReviewDataError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    write_jsonl(args.packet_output, packets)
    write_jsonl(args.key_output, keys)
    print(f"prepared {len(packets)} blinded pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
