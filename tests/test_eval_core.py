import unittest

from harness.eval_core import _paired_difference, apply_release_policy, score_results, validate_case

DATASET_VERSION = "2.0.0"
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
        "loaded_resources": (
            ["SKILL.md", "references/naming-model.md"] if variant != "without-skill" else []
        ),
        "usage": {
            "input_tokens": 90 if variant == "with-skill" else 100,
            "output_tokens": 10,
            "latency_ms": 10,
            "cost_usd": 0,
            "skill_context_words": 50
            if variant == "with-skill"
            else 100
            if variant == "previous-skill"
            else 0,
            "turns": 1,
            "tool_calls": 0,
        },
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
        "schema_version": "2.0",
        "dataset_version": DATASET_VERSION,
        "name": "test",
        "version": "2.0.0",
        "required_variants": ["with-skill", "previous-skill", "without-skill"],
        "gated_variant": "with-skill",
        "minimum_systems": 1,
        "minimum_replicates": minimum_replicates,
        "activation": {"minimum_accuracy": 1.0},
        "behavior": {"minimum_pass_rate": 1.0, "maximum_ungraded": 0},
        "comparison": {
            "baseline_variant": "without-skill",
            "minimum_activation_accuracy_delta": 0.0,
            "minimum_behavior_pass_rate_delta": 0.0,
        },
        "efficiency": {
            "comparison_variant": "previous-skill",
            "required_usage_fields": [
                "input_tokens",
                "output_tokens",
                "latency_ms",
                "skill_context_words",
                "turns",
                "tool_calls",
            ],
            "minimum_resource_reporting_rate": 1.0,
            "minimum_core_resource_rate": 1.0,
            "maximum_unknown_resources": 0,
            "maximum_unnecessary_resources": 0,
            "maximum_overloaded_profile_results": 0,
            "maximum_unexpected_activation_resource_results": 0,
            "maximum_input_token_ratio": 0.95,
            "maximum_skill_context_word_ratio": 0.6,
            "maximum_turn_ratio": 1.0,
        },
        "required_implementation_fields": [
            "adapter",
            "adapter_version",
            "agent",
            "agent_version",
            "model",
            "model_version",
            "reasoning",
        ],
    }


class EvalCoreTest(unittest.TestCase):
    def test_paired_interval_resamples_case_clusters(self):
        outcomes = {
            ("r1", "case-a", "i1"): {"with-skill": 1, "without-skill": 0},
            ("r1", "case-a", "i2"): {"with-skill": 1, "without-skill": 0},
            ("r1", "case-b", "i1"): {"with-skill": 0, "without-skill": 1},
        }
        comparison = _paired_difference(outcomes)
        self.assertEqual(comparison["clusters"], 2)
        self.assertEqual(comparison["matched_pairs"], 3)
        self.assertEqual(
            comparison["method"],
            "paired-case-cluster-percentile-bootstrap-95",
        )

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
        ungraded = score_results(
            cases, [result("B01", output_text="candidate", invariant_grades={})]
        )
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
            [
                result(
                    "B01",
                    output_text="candidate",
                    invariant_grades={"b01-01": "pass"},
                    observed_decisions=["map"],
                )
            ],
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

    def test_release_policy_rejects_configuration_drift_within_a_system(self):
        cases = {"T01": activation_case()}
        results = [
            result("T01", variant="with-skill", selected_skill=True),
            result(
                "T01",
                variant="previous-skill",
                selected_skill=True,
                configuration_hash="b" * 64,
            ),
            result("T01", variant="without-skill", selected_skill=True),
        ]
        evaluated = apply_release_policy(
            score_results(cases, results, require_complete=True), policy()
        )
        self.assertIn(
            "configuration changed across variants or replicates",
            "\n".join(evaluated["policy"]["violations"]),
        )

    def test_release_policy_links_scored_runs_to_verified_experiment(self):
        cases = {"T01": activation_case()}
        results = [
            result("T01", variant=variant, selected_skill=True)
            for variant in ("with-skill", "previous-skill", "without-skill")
        ]
        raw = score_results(cases, results, require_complete=True)
        raw["experiment_verification"] = {
            "valid": True,
            "experiment_id": "different-run",
            "dataset_version": DATASET_VERSION,
            "purpose": "release-candidate",
            "held_out_dataset_present": True,
        }
        release_policy = policy()
        release_policy["experiment"] = {
            "require_verified_preregistration": True,
            "require_release_candidate": True,
            "require_held_out_dataset": True,
        }
        evaluated = apply_release_policy(raw, release_policy)
        self.assertIn(
            "scored run IDs do not match the verified experiment",
            "\n".join(evaluated["policy"]["violations"]),
        )

    def test_policy_gates_candidate_while_comparing_control(self):
        cases = {"T01": activation_case(), "B01": behavior_case()}
        results = []
        for variant in ("with-skill", "previous-skill", "without-skill"):
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

    def test_policy_rejects_skill_resources_on_negative_activation(self):
        cases = {"T02": activation_case("T02", expected=False), "B01": behavior_case()}
        results = []
        for variant in ("with-skill", "previous-skill", "without-skill"):
            results.extend(
                [
                    result("T02", variant=variant, selected_skill=False),
                    result(
                        "B01",
                        variant=variant,
                        output_text="candidate",
                        invariant_grades={"b01-01": "pass"},
                        observed_decisions=["map"],
                    ),
                ]
            )
        evaluated = apply_release_policy(
            score_results(cases, results, require_complete=True), policy()
        )
        self.assertIn(
            "unexpected activation resource results 1 exceeds 0",
            "\n".join(evaluated["policy"]["violations"]),
        )

    def test_policy_rejects_known_but_unnecessary_behavior_resource(self):
        cases = {"T01": activation_case(), "B01": behavior_case()}
        results = []
        for variant in ("with-skill", "previous-skill", "without-skill"):
            behavior_result = result(
                "B01",
                variant=variant,
                output_text="candidate",
                invariant_grades={"b01-01": "pass"},
                observed_decisions=["map"],
            )
            if variant == "with-skill":
                behavior_result["loaded_resources"].append("references/systems-languages.md")
            results.extend([result("T01", variant=variant, selected_skill=True), behavior_result])
        evaluated = apply_release_policy(
            score_results(cases, results, require_complete=True), policy()
        )
        self.assertIn(
            "unnecessary loaded resources 1 exceeds 0",
            "\n".join(evaluated["policy"]["violations"]),
        )


if __name__ == "__main__":
    unittest.main()
