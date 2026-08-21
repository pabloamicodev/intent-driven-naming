import unittest

from harness.eval_core import apply_release_policy, score_results, validate_case


class EvalCoreTest(unittest.TestCase):
    def test_validates_activation_case(self):
        case = {
            "schema_version": "1.0",
            "id": "T01",
            "suite": "activation",
            "title": "Trigger",
            "prompt": "Improve these identifiers.",
            "tags": ["activation"],
            "expected_activation": True,
            "rationale": "Naming task.",
        }
        self.assertEqual(validate_case(case), [])

    def test_critical_failure_fails_hard_gate(self):
        cases = {
            "B01": {
                "schema_version": "1.0",
                "id": "B01",
                "suite": "behavior",
                "title": "Contract",
                "prompt": "Preserve the field.",
                "tags": ["contract"],
                "invariants": [
                    {
                        "id": "b01-01",
                        "description": "Serialized field remains unchanged.",
                        "severity": "critical",
                        "grading": "deterministic",
                    }
                ],
            }
        }
        results = [
            {
                "schema_version": "1.0",
                "run_id": "test",
                "case_id": "B01",
                "variant": "with-skill",
                "status": "completed",
                "invariant_grades": {"b01-01": "fail"},
            }
        ]
        report = score_results(cases, results)
        self.assertFalse(report["hard_gate_passed"])
        self.assertEqual(report["behavior"]["with-skill"]["critical_failures"], 1)

    def test_activation_metrics(self):
        cases = {
            "T01": {
                "schema_version": "1.0",
                "id": "T01",
                "suite": "activation",
                "title": "Positive",
                "prompt": "Rename a variable.",
                "tags": ["activation"],
                "expected_activation": True,
                "rationale": "Naming task.",
            },
            "T02": {
                "schema_version": "1.0",
                "id": "T02",
                "suite": "activation",
                "title": "Negative",
                "prompt": "Name a product.",
                "tags": ["activation"],
                "expected_activation": False,
                "rationale": "Brand task.",
            },
        }
        results = [
            {
                "schema_version": "1.0",
                "run_id": "test",
                "case_id": case_id,
                "variant": "with-skill",
                "status": "completed",
                "selected_skill": selected,
            }
            for case_id, selected in (("T01", True), ("T02", False))
        ]
        report = score_results(cases, results)
        self.assertEqual(report["activation"]["with-skill"]["accuracy"], 1.0)

    def test_ungraded_critical_invariant_fails_hard_gate(self):
        cases = {
            "B01": {
                "schema_version": "1.0",
                "id": "B01",
                "suite": "behavior",
                "title": "Contract",
                "prompt": "Preserve the field.",
                "tags": ["contract"],
                "invariants": [
                    {
                        "id": "b01-01",
                        "description": "Serialized field remains unchanged.",
                        "severity": "critical",
                        "grading": "semantic",
                    }
                ],
            }
        }
        results = [
            {
                "schema_version": "1.0",
                "run_id": "test",
                "case_id": "B01",
                "variant": "with-skill",
                "status": "completed",
                "invariant_grades": {},
            }
        ]
        report = score_results(cases, results)
        self.assertFalse(report["hard_gate_passed"])
        self.assertEqual(report["behavior"]["with-skill"]["critical_ungraded"], 1)

    def test_complete_scoring_rejects_partial_runs(self):
        cases = {
            case_id: {
                "schema_version": "1.0",
                "id": case_id,
                "suite": "activation",
                "title": case_id,
                "prompt": "Rename a variable.",
                "tags": ["activation"],
                "expected_activation": True,
                "rationale": "Naming task.",
            }
            for case_id in ("T01", "T02")
        }
        results = [
            {
                "schema_version": "1.0",
                "run_id": "test",
                "case_id": "T01",
                "variant": "with-skill",
                "status": "completed",
                "selected_skill": True,
            }
        ]
        report = score_results(cases, results, require_complete=True)
        self.assertFalse(report["hard_gate_passed"])
        self.assertEqual(
            report["completion"]["with-skill"]["incomplete_case_ids"], ["T02"]
        )

    def test_release_policy_rejects_missing_baseline_and_metadata(self):
        cases = {
            "T01": {
                "schema_version": "1.0",
                "id": "T01",
                "suite": "activation",
                "title": "Trigger",
                "prompt": "Rename this variable.",
                "tags": ["activation"],
                "expected_activation": True,
                "rationale": "Naming task.",
            }
        }
        results = [
            {
                "schema_version": "1.0",
                "run_id": "test",
                "case_id": "T01",
                "variant": "with-skill",
                "status": "completed",
                "selected_skill": True,
                "implementation": {"model": "example"},
            }
        ]
        report = score_results(cases, results, require_complete=True)
        policy = {
            "schema_version": "1.0",
            "name": "test",
            "version": "1.0.0",
            "required_variants": ["with-skill", "without-skill"],
            "gated_variant": "with-skill",
            "activation_minimums": {"recall": 0.9},
            "behavior": {},
            "comparison": {"baseline_variant": "without-skill"},
            "required_implementation_fields": ["model", "model_version"],
        }
        evaluated = apply_release_policy(report, policy)
        self.assertFalse(evaluated["hard_gate_passed"])
        self.assertIn(
            "without-skill: required variant is incomplete",
            evaluated["policy"]["violations"],
        )
        self.assertIn(
            "with-skill: implementation field model_version is incomplete",
            evaluated["policy"]["violations"],
        )

    def test_release_policy_gates_candidate_not_expected_baseline_failures(self):
        cases = {
            "T01": {
                "schema_version": "1.0",
                "id": "T01",
                "suite": "activation",
                "title": "Trigger",
                "prompt": "Rename this variable.",
                "tags": ["activation"],
                "expected_activation": True,
                "rationale": "Naming task.",
            },
            "B01": {
                "schema_version": "1.0",
                "id": "B01",
                "suite": "behavior",
                "title": "Contract",
                "prompt": "Preserve the field.",
                "tags": ["contract"],
                "invariants": [
                    {
                        "id": "b01-01",
                        "description": "Serialized field remains unchanged.",
                        "severity": "critical",
                        "grading": "semantic",
                    }
                ],
            },
        }
        results = []
        for variant in ("with-skill", "without-skill"):
            results.extend(
                [
                    {
                        "schema_version": "1.0",
                        "run_id": "test",
                        "case_id": "T01",
                        "variant": variant,
                        "status": "completed",
                        "selected_skill": True,
                        "implementation": {"adapter": "test"},
                    },
                    {
                        "schema_version": "1.0",
                        "run_id": "test",
                        "case_id": "B01",
                        "variant": variant,
                        "status": "completed",
                        "invariant_grades": {
                            "b01-01": "pass" if variant == "with-skill" else "fail"
                        },
                        "implementation": {"adapter": "test"},
                    },
                ]
            )
        raw_report = score_results(cases, results, require_complete=True)
        self.assertFalse(raw_report["hard_gate_passed"])
        evaluated = apply_release_policy(
            raw_report,
            {
                "schema_version": "1.0",
                "name": "test",
                "version": "1.0.0",
                "required_variants": ["with-skill", "without-skill"],
                "gated_variant": "with-skill",
                "activation_minimums": {"precision": 1.0, "recall": 1.0, "accuracy": 1.0},
                "behavior": {"minimum_pass_rate": 1.0, "maximum_ungraded": 0},
                "comparison": {
                    "baseline_variant": "without-skill",
                    "minimum_activation_accuracy_delta": 0.0,
                    "minimum_behavior_pass_rate_delta": 0.0,
                },
                "required_implementation_fields": ["adapter"],
            },
        )
        self.assertTrue(evaluated["hard_gate_passed"])


if __name__ == "__main__":
    unittest.main()
