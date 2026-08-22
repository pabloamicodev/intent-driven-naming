#!/usr/bin/env python3
"""Create blinded semantic-review packets and a separate reidentification key."""

from __future__ import annotations

import argparse
import secrets
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.eval_core import EvaluationDataError, load_case_map, read_jsonl, write_jsonl
from harness.review_core import ReviewDataError, prepare_review_packet

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, nargs="+", required=True)
    parser.add_argument("--behavior-cases", type=Path, default=ROOT / "evals/cases/behavior.jsonl")
    parser.add_argument("--packet-output", type=Path, required=True)
    parser.add_argument("--key-output", type=Path, required=True)
    parser.add_argument(
        "--artifact-root",
        type=Path,
        help="explicit root containing sanitized artifact bundle paths referenced by results",
    )
    parser.add_argument("--salt", default=None, help="optional reproducibility salt; omit for a random salt")
    args = parser.parse_args()

    try:
        cases = load_case_map([args.behavior_cases])
        results = [record for path in args.results for record in read_jsonl(path)]
        packets, keys = prepare_review_packet(
            cases,
            results,
            args.salt or secrets.token_hex(32),
            artifact_root=args.artifact_root,
        )
    except (EvaluationDataError, ReviewDataError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    write_jsonl(args.packet_output, packets)
    write_jsonl(args.key_output, keys)
    print(f"wrote {len(packets)} blinded review packets and {len(keys)} private keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
