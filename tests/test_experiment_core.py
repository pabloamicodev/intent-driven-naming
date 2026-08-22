import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.experiment_core import execution_jobs, load_experiment, validate_experiment
from harness.freeze_experiment import freeze_manifest

ROOT = Path(__file__).resolve().parents[1]


class ExperimentCoreTest(unittest.TestCase):
    def test_checked_in_development_experiment_is_frozen_and_plannable(self):
        manifest_path = ROOT / "examples" / "experiment-manifest.json"
        config_path = ROOT / "examples" / "runner-config.json"
        manifest, config = load_experiment(manifest_path, config_path)
        validation = validate_experiment(
            manifest,
            config,
            runner_config_path=config_path,
        )
        self.assertEqual(validation["errors"], [])
        self.assertEqual(len(execution_jobs(manifest, validation)), 6)
        self.assertEqual(
            freeze_manifest(manifest, config, runner_config_path=config_path),
            manifest,
        )

    def test_release_candidate_requires_held_out_data_and_distinct_systems(self):
        manifest_path = ROOT / "examples" / "experiment-manifest.json"
        config_path = ROOT / "examples" / "runner-config.json"
        manifest, config = load_experiment(manifest_path, config_path)
        manifest["purpose"] = "release-candidate"
        manifest["claim_scope"] = "organization-grade-candidate"
        manifest["replicate_ids"] = ["r1", "r2", "r3"]
        manifest["systems"] = [manifest["systems"][0]] * 3
        validation = validate_experiment(
            manifest,
            config,
            runner_config_path=config_path,
        )
        joined = "\n".join(validation["errors"])
        self.assertIn("duplicate system system_id", joined)
        self.assertIn("held-out dataset", joined)

    def test_malformed_collections_return_errors_instead_of_crashing(self):
        manifest_path = ROOT / "examples" / "experiment-manifest.json"
        config_path = ROOT / "examples" / "runner-config.json"
        manifest, config = load_experiment(manifest_path, config_path)
        manifest["variants"] = [{}]
        manifest["replicate_ids"] = [{}]
        manifest["systems"] = [None]
        manifest["datasets"] = [None]
        validation = validate_experiment(
            manifest,
            config,
            runner_config_path=config_path,
        )
        self.assertTrue(validation["errors"])

    def test_mock_matrix_executes_and_verifies_end_to_end(self):
        manifest_path = ROOT / "examples" / "experiment-manifest.json"
        source_config = json.loads(
            (ROOT / "examples" / "runner-config.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            source_config["output_root"] = str(temporary / "results")
            source_config["current_skill_path"] = str(ROOT)
            source_config["baseline_skill_path"] = str(ROOT)
            source_config["release_policy_path"] = str(
                ROOT / "specification" / "release-policy.json"
            )
            source_config["datasets"][0]["activation_cases"] = str(
                ROOT / "evals" / "cases" / "activation.jsonl"
            )
            source_config["datasets"][0]["behavior_cases"] = str(
                ROOT / "evals" / "cases" / "behavior.jsonl"
            )
            config_path = temporary / "runner.json"
            config_path.write_text(json.dumps(source_config), encoding="utf-8")
            execute = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "harness" / "run_experiment.py"),
                    "--manifest",
                    str(manifest_path),
                    "--runner-config",
                    str(config_path),
                    "--execute",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(execute.returncode, 0, execute.stderr)
            experiment_root = temporary / "results" / "idn-public-development-2.0.0"
            verify = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "harness" / "verify_experiment.py"),
                    "--manifest",
                    str(manifest_path),
                    "--runner-config",
                    str(config_path),
                    "--experiment-root",
                    str(experiment_root),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(verify.returncode, 0, verify.stderr)
            self.assertTrue(json.loads(verify.stdout)["valid"])

    def test_resume_requires_a_preregistered_retry_reason_after_failure(self):
        manifest_path = ROOT / "examples" / "experiment-manifest.json"
        source_config = json.loads(
            (ROOT / "examples" / "runner-config.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            source_config["output_root"] = str(temporary / "results")
            source_config["current_skill_path"] = str(ROOT)
            source_config["baseline_skill_path"] = str(ROOT)
            source_config["release_policy_path"] = str(
                ROOT / "specification" / "release-policy.json"
            )
            source_config["datasets"][0]["activation_cases"] = str(
                ROOT / "evals" / "cases" / "activation.jsonl"
            )
            source_config["datasets"][0]["behavior_cases"] = str(
                ROOT / "evals" / "cases" / "behavior.jsonl"
            )
            source_config["adapters"][0]["command"] = [
                "${PYTHON}",
                str(ROOT / "tests" / "fixtures" / "spoof_adapter.py"),
            ]
            config_path = temporary / "runner.json"
            config_path.write_text(json.dumps(source_config), encoding="utf-8")
            base_command = [
                sys.executable,
                str(ROOT / "harness" / "run_experiment.py"),
                "--manifest",
                str(manifest_path),
                "--runner-config",
                str(config_path),
                "--execute",
            ]
            failed = subprocess.run(
                base_command,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(failed.returncode, 1)
            resumed = subprocess.run(
                [*base_command, "--resume"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(resumed.returncode, 2)
            self.assertIn("--retry-reason is required", resumed.stderr)


if __name__ == "__main__":
    unittest.main()
