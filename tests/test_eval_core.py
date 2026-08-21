import unittest

from harness.eval_core import apply_release_policy, score_results, validate_case


DATASET_VERSION = "1.1.0"
HASH = "a" * 64
COHORT = "test-system::with-skill"


def activation_case(case_id="T01", expected=True, difficulty="standard", locale="en"):
    return {
        "schema_version": "1.0",
        "dataset_version": DATASET_VERSION,
        "id": case_id,
        "suite": "activation",
        "title": case_id,
        "prompt": "Improve these identifiers." if expected else "Name a product.",
        "difficulty": difficulty,
        "locale": locale,
        "tags": ["activation"],
        "expected_activation": expected,
        "rationale": "Naming task." if expected else "Out of scope.",
    }


def behavior_case():
    return {
        "schema_version": "1.0",
        "dataset_version": DATASET_VERSION,
        "id": "B01",
        "suite": "behavior",
        "title": "Contract",
        "prompt": "Preserve the wire field and improve the internal name.",
        "difficulty": "edge",
        "locale": "en",
        "mode": "refactor",
        "languages": ["typescript"],
        "contract_risk": "external",
        "expected_decisions": ["map"],
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


def result(case_id, variant="with-skill", replicate="r1", attempt=1, **overrides):
    record = {
        "schema_version": "1.0",
        "protocol_version": 1,
        "dataset_version": DATASET_VERSION,
        "run_id": "test-run",
        "system_id": "test-system",
        "configuration_hash": HASH,
        "replicate_id": replicate,
        "attempt": attempt,
        "case_id": case_id,
        "variant": variant,
        "status": "completed",
        "implementation": {
            "adapter": "test",
            "adapter_version": "1",
            "agent": "test",
            "agent_version": "1",
            "model": "test",
            "model_version": "1",
            "reasoning": "fixed",
        },
    }
    record.update(overrides)
    return record


def policy(minimum_replicates=1):
    return {
        "schema_version": "1.1",
        "dataset_version": DATASET_VERSION,
        "name": "test",
        "version": "1.1.0",
        "required_variants": ["with-skill", "without-skill"],
        "gated_variant": "with-skill",
        "minimum_replicates": minimum_replicates,
        "activation": {"minimum_accuracy": 1.0},
        "behavior": {"minimum_pass_rate": 1.0, "maximum_ungraded": 0},
        "comparison": {
            "baseline_variant": "without-skill",
            "minimum_activation_accuracy_delta": 0.0,
            "minimum_behavior_pass_rate_delta": 0.0,
        },
        "required_implementation_fields": [
            "adapter", "adapter_version", "agent", "agent_version", "model", "model_version", "reasoning"
        ],
    }


class EvalCoreTest(unittest.TestCase):
    def test_validates_activation_case(self):
        self.assertEqual(validate_case(activation_case()), [])

    def test_critical_failure_and_ungraded_critical_fail_hard_gate(self):
        cases = {"B01": behavior_case()}
        failed = score_results(
            cases,
            [result("B01", output_text="candidate", invariant_grades={"b01-01": "fail"})],
        )
        self.assertFalse(failed["hard_gate_passed"])
        self.assertEqual(failed["behavior"][COHORT]["critical_failures"], 1)
        ungraded = score_results(cases, [result("B01", output_text="candidate", invariant_grades={})])
        self.assertFalse(ungraded["hard_gate_passed"])
        self.assertEqual(ungraded["behavior"][COHORT]["critical_ungraded"], 1)

    def test_activation_metrics_slices_and_specificity(self):
        cases = {
            "T01": activation_case("T01", True, "standard", "en"),
            "T02": activation_case("T02", False, "adversarial", "es"),
        }
        report = score_results(
            cases,
            [result("T01", selected_skill=True), result("T02", selected_skill=False)],
        )
        metrics = report["activation"][COHORT]
        self.assertEqual(metrics["specificity"], 1.0)
        self.assertEqual(metrics["balanced_accuracy"], 1.0)
        self.assertIn("locale:es", report["activation_by_slice"][COHORT])

    def test_complete_scoring_is_per_replicate(self):
        cases = {case_id: activation_case(case_id) for case_id in ("T01", "T02")}
        report = score_results(cases, [result("T01", selected_skill=True)], require_complete=True)
        self.assertFalse(report["hard_gate_passed"])
        completion = report["completion"][f"{COHORT}::r1"]
        self.assertEqual(completion["incomplete_case_ids"], ["T02"])

    def test_highest_retry_attempt_is_scored(self):
        cases = {"T01": activation_case()}
        report = score_results(
            cases,
            [
                result("T01", attempt=1, selected_skill=False),
                result("T01", attempt=2, selected_skill=True),
            ],
        )
        self.assertEqual(report["activation"][COHORT]["tp"], 1)
        self.assertEqual(report["retries"]["retried_case_runs"], 1)

    def test_decision_exact_match_is_reported(self):
        cases = {"B01": behavior_case()}
        report = score_results(
            cases,
            [result("B01", output_text="candidate", invariant_grades={"b01-01": "pass"}, observed_decisions=["map"])],
        )
        self.assertEqual(report["decisions"][COHORT]["exact_match_rate"], 1.0)

    def test_release_policy_rejects_missing_control_and_replicates(self):
        cases = {"T01": activation_case()}
        raw = score_results(cases, [result("T01", selected_skill=True)], require_complete=True)
        evaluated = apply_release_policy(raw, policy(minimum_replicates=2))
        self.assertFalse(evaluated["hard_gate_passed"])
        violations = "\n".join(evaluated["policy"]["violations"])
        self.assertIn("without-skill: required cohort is missing", violations)
        self.assertIn("replicates is below 2", violations)

    def test_policy_gates_candidate_while_comparing_control(self):
        cases = {"T01": activation_case(), "B01": behavior_case()}
        results = []
        for variant in ("with-skill", "without-skill"):
            results.extend(
                [
                    result("T01", variant=variant, selected_skill=True),
                    result(
                        "B01",
                        variant=variant,
                        output_text="candidate",
                        invariant_grades={"b01-01": "pass" if variant == "with-skill" else "fail"},
                        observed_decisions=["map"],
                    ),
                ]
            )
        raw = score_results(cases, results, require_complete=True)
        self.assertFalse(raw["hard_gate_passed"])
        evaluated = apply_release_policy(raw, policy())
        self.assertTrue(evaluated["hard_gate_passed"])
        tie_rejecting_policy = policy()
        tie_rejecting_policy["comparison"]["minimum_activation_accuracy_delta"] = 0.01
        tie_rejected = apply_release_policy(raw, tie_rejecting_policy)
        self.assertFalse(tie_rejected["hard_gate_passed"])
        self.assertIn(
            "activation_accuracy delta 0.0 is below 0.01",
            "\n".join(tie_rejected["policy"]["violations"]),
        )


if __name__ == "__main__":
    unittest.main()
