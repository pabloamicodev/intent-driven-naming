"""End-to-end CLI coverage for the human-review wiring:

prepare_review.py -> merge_reviews.py and
prepare_pairwise_review.py -> score_pairwise.py.

The underlying scoring logic already has direct unit tests in
test_review_core.py and test_pairwise_core.py; these tests exercise the
argparse wiring, file I/O, and exit codes of the CLI scripts themselves.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.eval_core import read_jsonl

ROOT = Path(__file__).resolve().parents[1]


def _behavior_case() -> dict:
    return {
        "schema_version": "1.0",
        "dataset_version": "test-1.0",
        "id": "B01",
        "suite": "behavior",
        "title": "Protect a contract",
        "prompt": "Refactor this code.",
        "locale": "en",
        "difficulty": "standard",
        "tags": ["contract"],
        "mode": "refactor",
        "contract_risk": "internal",
        "languages": ["python"],
        "expected_decisions": ["rename"],
        "invariants": [
            {
                "id": "b01-1",
                "description": "Behavior remains unchanged.",
                "severity": "major",
                "grading": "semantic",
            }
        ],
    }


def _result(*, variant: str, output_text: str) -> dict:
    return {
        "schema_version": "1.0",
        "protocol_version": 1,
        "dataset_version": "test-1.0",
        "run_id": "run-1",
        "system_id": "test-system",
        "configuration_hash": "a" * 64,
        "replicate_id": "r1",
        "attempt": 1,
        "case_id": "B01",
        "variant": variant,
        "status": "completed",
        "output_text": output_text,
        "implementation": {"adapter": "test"},
    }


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True
    )


class ReviewPipelineCliTest(unittest.TestCase):
    def test_prepare_review_then_merge_reviews(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            behavior_cases = directory / "behavior.jsonl"
            behavior_cases.write_text(json.dumps(_behavior_case()) + "\n", encoding="utf-8")
            results_path = directory / "results.jsonl"
            results_path.write_text(
                json.dumps(_result(variant="with-skill", output_text="candidate output")) + "\n",
                encoding="utf-8",
            )
            packets_path = directory / "packets.jsonl"
            keys_path = directory / "keys.jsonl"
            prepared = _run(
                str(ROOT / "harness" / "prepare_review.py"),
                "--results",
                str(results_path),
                "--behavior-cases",
                str(behavior_cases),
                "--packet-output",
                str(packets_path),
                "--key-output",
                str(keys_path),
                "--salt",
                "fixed-test-salt",
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            packets = read_jsonl(packets_path)
            keys = read_jsonl(keys_path)
            self.assertEqual(len(packets), 1)
            self.assertNotIn("variant", packets[0])
            review_id = keys[0]["review_id"]

            reviews_path = directory / "reviews.jsonl"
            reviews_path.write_text(
                "\n".join(
                    json.dumps(
                        {
                            "schema_version": "1.1",
                            "review_id": review_id,
                            "reviewer_id": reviewer_id,
                            "reviewer_kind": "human",
                            "grades": {"b01-1": "pass"},
                            "evidence": {"b01-1": "The behavior is observably unchanged."},
                            "observed_decisions": ["rename"],
                        }
                    )
                    for reviewer_id in ("reviewer-one", "reviewer-two")
                )
                + "\n",
                encoding="utf-8",
            )
            merged_path = directory / "merged.jsonl"
            agreement_path = directory / "agreement.json"
            merged = _run(
                str(ROOT / "harness" / "merge_reviews.py"),
                "--results",
                str(results_path),
                "--review-keys",
                str(keys_path),
                "--reviews",
                str(reviews_path),
                "--output",
                str(merged_path),
                "--agreement-output",
                str(agreement_path),
                "--behavior-cases",
                str(behavior_cases),
                "--minimum-reviews",
                "2",
            )
            self.assertEqual(merged.returncode, 0, merged.stderr)
            merged_results = read_jsonl(merged_path)
            self.assertEqual(merged_results[0]["invariant_grades"], {"b01-1": "pass"})
            agreement = json.loads(agreement_path.read_text(encoding="utf-8"))
            self.assertEqual(agreement["raw_grade_agreement"], 1.0)
            self.assertEqual(agreement["agreement_population"], "human")

    def test_prepare_pairwise_review_then_score_pairwise(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            behavior_cases = directory / "behavior.jsonl"
            behavior_cases.write_text(json.dumps(_behavior_case()) + "\n", encoding="utf-8")
            results_path = directory / "results.jsonl"
            results_path.write_text(
                "\n".join(
                    json.dumps(_result(variant=variant, output_text=f"candidate {variant}"))
                    for variant in ("with-skill", "without-skill")
                )
                + "\n",
                encoding="utf-8",
            )
            packets_path = directory / "pairwise-packets.jsonl"
            keys_path = directory / "pairwise-keys.jsonl"
            prepared = _run(
                str(ROOT / "harness" / "prepare_pairwise_review.py"),
                "--results",
                str(results_path),
                "--behavior-cases",
                str(behavior_cases),
                "--salt",
                "fixed-pairwise-salt",
                "--packet-output",
                str(packets_path),
                "--key-output",
                str(keys_path),
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            keys = read_jsonl(keys_path)
            self.assertEqual(len(keys), 1)
            winning_label = "A" if keys[0]["A_variant"] == "with-skill" else "B"

            reviews_path = directory / "pairwise-reviews.jsonl"
            reviews_path.write_text(
                "\n".join(
                    json.dumps(
                        {
                            "schema_version": "1.1",
                            "pair_id": keys[0]["pair_id"],
                            "reviewer_id": reviewer_id,
                            "reviewer_kind": "human",
                            "preference": winning_label,
                            "evidence": "The with-skill candidate is safer and clearer.",
                        }
                    )
                    for reviewer_id in ("reviewer-one", "reviewer-two")
                )
                + "\n",
                encoding="utf-8",
            )
            report_path = directory / "pairwise-report.json"
            scored = _run(
                str(ROOT / "harness" / "score_pairwise.py"),
                "--keys",
                str(keys_path),
                "--reviews",
                str(reviews_path),
                "--output",
                str(report_path),
            )
            self.assertEqual(scored.returncode, 0, scored.stderr)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["with_skill_wins"], 1)
            self.assertEqual(report["unresolved"], 0)


if __name__ == "__main__":
    unittest.main()
