import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.score_results import markdown_report

ROOT = Path(__file__).resolve().parents[1]


def _case(case_id: str, *, suite: str, **overrides) -> dict:
    base = {
        "schema_version": "1.0",
        "dataset_version": "test-1.0",
        "id": case_id,
        "suite": suite,
        "title": "Case title",
        "prompt": "Improve this code.",
        "locale": "en",
        "difficulty": "standard",
        "tags": ["contract"],
    }
    base.update(overrides)
    return base


def _result(case_id: str, *, variant: str, **overrides) -> dict:
    base = {
        "schema_version": "1.0",
        "protocol_version": 1,
        "dataset_version": "test-1.0",
        "run_id": "run-1",
        "system_id": "test-system",
        "configuration_hash": "a" * 64,
        "replicate_id": "r1",
        "attempt": 1,
        "case_id": case_id,
        "variant": variant,
        "status": "completed",
    }
    base.update(overrides)
    return base


class MarkdownReportTest(unittest.TestCase):
    def test_renders_every_section_for_pass_and_fail_cohorts(self):
        report = {
            "hard_gate_passed": False,
            "errors": ["T01: unknown case_id"],
            "policy": {
                "name": "release-gate",
                "version": "1.0",
                "passed": False,
                "violations": ["candidate: behavior pass_rate 0.5 is below 0.9"],
                "observations": {"candidate:input_tokens_ratio": 1.2},
            },
            "completion": {
                "test-system::with-skill::r1": {
                    "completed_cases": 1,
                    "expected_cases": 2,
                    "complete": False,
                }
            },
            "activation": {
                "test-system::with-skill": {
                    "precision": 1.0,
                    "recall": 0.5,
                    "specificity": 1.0,
                    "balanced_accuracy": 0.75,
                    "accuracy": 0.8,
                    "accuracy_confidence_interval_95": [0.4, 1.0],
                    "false_positive_rate": 0.0,
                }
            },
            "behavior": {
                "test-system::with-skill": {
                    "pass_rate": 0.5,
                    "case_pass_rate": 0.5,
                    "critical_failures": 1,
                    "critical_ungraded": 0,
                    "ungraded": 0,
                    "hard_gate_passed": False,
                }
            },
            "decisions": {
                "test-system::with-skill": {
                    "exact_match_rate": 1.0,
                    "graded_cases": 1,
                    "ungraded_cases": 0,
                }
            },
            "review_agreement": {
                "minimum_reviews_per_candidate": 2,
                "minimum_human_reviews_per_candidate": 2,
                "raw_grade_agreement": 1.0,
                "chance_corrected_grade_agreement": 1.0,
                "decision_set_agreement": 1.0,
            },
            "pairwise_report": {
                "resolved_fraction": 1.0,
                "with_skill_win_rate_excluding_ties": 0.75,
                "minimum_human_reviews_per_pair": 2,
            },
            "experiment_verification": {
                "experiment_id": "exp-2026-01",
                "valid": True,
                "purpose": "release-candidate",
                "held_out_dataset_present": True,
                "systems": 1,
                "replicates": 3,
            },
            "configuration_integrity": {
                "test-system": {"consistent_across_variants_and_replicates": True}
            },
            "usage": {
                "test-system::with-skill": {
                    "completed_results": 1,
                    "input_tokens": {"total": 100},
                    "output_tokens": {"total": 50},
                    "skill_context_words": {"total": 400},
                    "turns": {"total": 1},
                    "tool_calls": {"total": 2},
                    "latency_ms": {"total": 900},
                    "cost_usd": {"total": 0.01},
                }
            },
            "resource_loading": {
                "test-system::with-skill": {
                    "reporting_rate": 1.0,
                    "core_complete_rate": 1.0,
                    "mean_resources_per_result": 2.0,
                    "unknown_resources": {"references/ghost.md": 1},
                    "unexpected_activation_resource_results": 0,
                }
            },
            "by_tag": {
                "test-system::with-skill:contract": {
                    "pass": 1,
                    "fail": 1,
                    "pass_rate": 0.5,
                }
            },
        }
        rendered = markdown_report(report)
        self.assertTrue(rendered.startswith("# Evaluation Report"))
        self.assertIn("Hard gate: FAIL", rendered)
        self.assertIn("## Data Errors", rendered)
        self.assertIn("T01: unknown case_id", rendered)
        self.assertIn("## Release Policy", rendered)
        self.assertIn("candidate: behavior pass_rate 0.5 is below 0.9", rendered)
        self.assertIn("## Completion", rendered)
        self.assertIn("## Activation", rendered)
        self.assertIn("## Behavior", rendered)
        self.assertIn("## Decisions", rendered)
        self.assertIn("## Review Agreement", rendered)
        self.assertIn("## Pairwise Review", rendered)
        self.assertIn("## Preregistered Experiment", rendered)
        self.assertIn("## Configuration Integrity", rendered)
        self.assertIn("test-system: consistent", rendered)
        self.assertIn("## Usage", rendered)
        self.assertIn("## Resource Loading", rendered)
        self.assertIn("## Behavior by Tag", rendered)

    def test_omits_optional_sections_when_absent_and_reports_pass(self):
        report = {
            "hard_gate_passed": True,
            "errors": [],
            "completion": {},
            "activation": {},
            "behavior": {},
            "decisions": {},
            "usage": {},
            "by_tag": {},
        }
        rendered = markdown_report(report)
        self.assertIn("Hard gate: PASS", rendered)
        self.assertNotIn("## Release Policy", rendered)
        self.assertNotIn("## Review Agreement", rendered)
        self.assertNotIn("## Pairwise Review", rendered)
        self.assertNotIn("## Preregistered Experiment", rendered)
        self.assertNotIn("## Configuration Integrity", rendered)
        self.assertNotIn("## Resource Loading", rendered)


class ScoreResultsCliTest(unittest.TestCase):
    def _write_fixture_files(self, directory: Path) -> tuple[Path, Path, Path]:
        activation_cases = directory / "activation.jsonl"
        behavior_cases = directory / "behavior.jsonl"
        results = directory / "results.jsonl"
        activation_cases.write_text(
            json.dumps(
                _case(
                    "T01",
                    suite="activation",
                    expected_activation=True,
                    rationale="Naming task.",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        behavior_cases.write_text(
            json.dumps(
                _case(
                    "B01",
                    suite="behavior",
                    mode="refactor",
                    contract_risk="internal",
                    languages=["python"],
                    expected_decisions=["rename"],
                    invariants=[
                        {
                            "id": "b01-1",
                            "description": "Behavior remains unchanged.",
                            "severity": "major",
                            "grading": "deterministic",
                        }
                    ],
                )
            )
            + "\n",
            encoding="utf-8",
        )
        results.write_text(
            "\n".join(
                json.dumps(record)
                for record in (
                    _result("T01", variant="with-skill", selected_skill=True),
                    _result(
                        "B01",
                        variant="with-skill",
                        output_text="candidate output",
                        invariant_grades={"b01-1": "pass"},
                        observed_decisions=["rename"],
                    ),
                )
            )
            + "\n",
            encoding="utf-8",
        )
        return activation_cases, behavior_cases, results

    def test_reports_hard_gate_pass_and_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            activation_cases, behavior_cases, results = self._write_fixture_files(directory)
            json_output = directory / "report.json"
            markdown_output = directory / "report.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "harness" / "score_results.py"),
                    "--results",
                    str(results),
                    "--activation-cases",
                    str(activation_cases),
                    "--behavior-cases",
                    str(behavior_cases),
                    "--json-output",
                    str(json_output),
                    "--markdown-output",
                    str(markdown_output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(json_output.read_text(encoding="utf-8"))
            self.assertTrue(report["hard_gate_passed"])
            self.assertIn("# Evaluation Report", markdown_output.read_text(encoding="utf-8"))

    def test_rejects_malformed_review_agreement_attachment(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            activation_cases, behavior_cases, results = self._write_fixture_files(directory)
            review_agreement = directory / "agreement.json"
            review_agreement.write_text("[]", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "harness" / "score_results.py"),
                    "--results",
                    str(results),
                    "--activation-cases",
                    str(activation_cases),
                    "--behavior-cases",
                    str(behavior_cases),
                    "--review-agreement",
                    str(review_agreement),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("review agreement must be a JSON object", completed.stderr)

    def test_rejects_unreadable_pairwise_report_attachment(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            activation_cases, behavior_cases, results = self._write_fixture_files(directory)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "harness" / "score_results.py"),
                    "--results",
                    str(results),
                    "--activation-cases",
                    str(activation_cases),
                    "--behavior-cases",
                    str(behavior_cases),
                    "--pairwise-report",
                    str(directory / "missing.json"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("cannot load pairwise report", completed.stderr)


if __name__ == "__main__":
    unittest.main()
