import unittest

from harness.pairwise_core import prepare_pairwise_packet, score_pairwise


class PairwiseCoreTest(unittest.TestCase):
    def test_blinds_orientation_and_resolves_to_real_variant(self):
        case = {
            "schema_version": "1.0",
            "dataset_version": "1.1.0",
            "id": "B01",
            "suite": "behavior",
            "title": "Case",
            "prompt": "Improve names.",
            "difficulty": "standard",
            "locale": "en",
            "mode": "refactor",
            "languages": ["python"],
            "contract_risk": "internal",
            "expected_decisions": ["rename"],
            "tags": ["behavior"],
            "invariants": [
                {
                    "id": "b01-01",
                    "description": "Clearer name.",
                    "severity": "major",
                    "grading": "semantic",
                }
            ],
        }
        results = []
        for variant in ("with-skill", "without-skill"):
            results.append(
                {
                    "schema_version": "1.0",
                    "protocol_version": 1,
                    "dataset_version": "1.1.0",
                    "run_id": "run",
                    "system_id": "system",
                    "configuration_hash": "a" * 64,
                    "replicate_id": "r1",
                    "attempt": 1,
                    "case_id": "B01",
                    "variant": variant,
                    "status": "completed",
                    "output_text": "candidate one" if variant == "with-skill" else "candidate two",
                    "implementation": {"adapter": "test"},
                }
            )
        packets, keys = prepare_pairwise_packet({"B01": case}, results, "salt")
        self.assertEqual(len(packets), 1)
        self.assertNotIn("A_variant", packets[0])
        self.assertNotIn("B_variant", packets[0])
        self.assertEqual([candidate["label"] for candidate in packets[0]["candidates"]], ["A", "B"])
        winning_label = "A" if keys[0]["A_variant"] == "with-skill" else "B"
        reviews = [
            {
                "schema_version": "1.1",
                "pair_id": keys[0]["pair_id"],
                "reviewer_id": reviewer,
                "reviewer_kind": "human",
                "preference": winning_label,
                "evidence": "The safer and clearer candidate.",
            }
            for reviewer in ("one", "two")
        ]
        report = score_pairwise(keys, reviews)
        self.assertEqual(report["with_skill_wins"], 1)
        self.assertEqual(report["raw_reviewer_agreement"], 1.0)
        self.assertEqual(report["minimum_human_reviews_per_pair"], 2)
        losing_label = "B" if winning_label == "A" else "A"
        reviews.extend(
            {
                "schema_version": "1.1",
                "pair_id": keys[0]["pair_id"],
                "reviewer_id": reviewer,
                "reviewer_kind": "model",
                "preference": losing_label,
                "evidence": "Automated auxiliary preference.",
            }
            for reviewer in ("model-one", "model-two", "model-three")
        )
        human_first_report = score_pairwise(keys, reviews)
        self.assertEqual(human_first_report["with_skill_wins"], 1)
        self.assertEqual(human_first_report["agreement_population"], "human")


if __name__ == "__main__":
    unittest.main()
