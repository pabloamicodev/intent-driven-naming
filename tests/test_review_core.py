import unittest

from harness.review_core import merge_reviews, prepare_review_packet, review_agreement


class ReviewCoreTest(unittest.TestCase):
    def setUp(self):
        self.cases = {
            "B01": {
                "schema_version": "1.0",
                "dataset_version": "1.1.0",
                "id": "B01",
                "suite": "behavior",
                "title": "Protect a contract",
                "prompt": "Refactor this code.",
                "difficulty": "edge",
                "locale": "en",
                "mode": "refactor",
                "languages": ["typescript"],
                "contract_risk": "external",
                "expected_decisions": ["map"],
                "tags": ["contract"],
                "invariants": [
                    {
                        "id": "b01-critical",
                        "description": "The wire key remains stable.",
                        "severity": "critical",
                        "grading": "semantic",
                    },
                    {
                        "id": "b01-major",
                        "description": "The internal name becomes clearer.",
                        "severity": "major",
                        "grading": "semantic",
                    },
                ],
            }
        }
        self.results = [
            {
                "schema_version": "1.0",
                "protocol_version": 1,
                "dataset_version": "1.1.0",
                "run_id": "run-1",
                "system_id": "test-system",
                "configuration_hash": "a" * 64,
                "replicate_id": "r1",
                "attempt": 1,
                "case_id": "B01",
                "variant": "with-skill",
                "status": "completed",
                "output_text": "candidate output",
                "implementation": {"adapter": "test"},
            }
        ]

    def test_review_packet_hides_variant_run_and_expected_decisions(self):
        packets, keys = prepare_review_packet(self.cases, self.results, "fixed-salt")
        self.assertEqual(len(packets), 1)
        self.assertNotIn("variant", packets[0])
        self.assertNotIn("run_id", packets[0])
        self.assertNotIn("expected_decisions", packets[0]["case"])
        self.assertEqual(keys[0]["variant"], "with-skill")

    def test_critical_any_fail_noncritical_majority_and_agreement(self):
        _, keys = prepare_review_packet(self.cases, self.results, "fixed-salt")
        review_id = keys[0]["review_id"]
        reviews = []
        for index, (critical, major) in enumerate(
            (("pass", "pass"), ("fail", "fail"), ("pass", "pass")), start=1
        ):
            reviews.append(
                {
                    "schema_version": "1.1",
                    "review_id": review_id,
                    "reviewer_id": f"reviewer-{index}",
                    "reviewer_kind": "human",
                    "grades": {"b01-critical": critical, "b01-major": major},
                    "evidence": {
                        "b01-critical": "Observed boundary behavior in the candidate.",
                        "b01-major": "Observed internal identifier in the candidate.",
                    },
                    "observed_decisions": ["map"],
                }
            )
        merged = merge_reviews(self.cases, self.results, keys, reviews, minimum_reviews=2)
        self.assertEqual(merged[0]["invariant_grades"]["b01-critical"], "fail")
        self.assertEqual(merged[0]["invariant_grades"]["b01-major"], "pass")
        self.assertEqual(merged[0]["observed_decisions"], ["map"])
        agreement = review_agreement(self.cases, keys, reviews)
        self.assertEqual(agreement["minimum_reviews_per_candidate"], 3)
        self.assertEqual(agreement["minimum_human_reviews_per_candidate"], 3)
        self.assertEqual(agreement["decision_set_agreement"], 1.0)

    def test_model_graders_cannot_outvote_human_reviewers(self):
        _, keys = prepare_review_packet(self.cases, self.results, "fixed-salt")
        review_id = keys[0]["review_id"]
        reviews = []
        for reviewer_id in ("human-one", "human-two"):
            reviews.append(
                {
                    "schema_version": "1.1",
                    "review_id": review_id,
                    "reviewer_id": reviewer_id,
                    "reviewer_kind": "human",
                    "grades": {"b01-critical": "pass", "b01-major": "pass"},
                    "evidence": {
                        "b01-critical": "The protected boundary is unchanged.",
                        "b01-major": "The internal name communicates intent.",
                    },
                    "observed_decisions": ["map"],
                }
            )
        for reviewer_id in ("model-one", "model-two", "model-three"):
            reviews.append(
                {
                    "schema_version": "1.1",
                    "review_id": review_id,
                    "reviewer_id": reviewer_id,
                    "reviewer_kind": "model",
                    "grades": {"b01-critical": "fail", "b01-major": "fail"},
                    "evidence": {
                        "b01-critical": "Automated auxiliary assessment.",
                        "b01-major": "Automated auxiliary assessment.",
                    },
                    "observed_decisions": ["rename"],
                }
            )
        merged = merge_reviews(self.cases, self.results, keys, reviews, minimum_reviews=2)
        self.assertEqual(merged[0]["invariant_grades"]["b01-critical"], "pass")
        self.assertEqual(merged[0]["invariant_grades"]["b01-major"], "pass")
        self.assertEqual(merged[0]["observed_decisions"], ["map"])
        agreement = review_agreement(self.cases, keys, reviews)
        self.assertEqual(agreement["agreement_population"], "human")
        self.assertEqual(agreement["raw_grade_agreement"], 1.0)


if __name__ == "__main__":
    unittest.main()
