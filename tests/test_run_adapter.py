import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.eval_core import read_jsonl

ROOT = Path(__file__).resolve().parents[1]


class RunAdapterTest(unittest.TestCase):
    def test_runs_jsonl_adapter_without_shell(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "results.jsonl"
            command = [
                sys.executable,
                str(ROOT / "harness" / "run_adapter.py"),
                "--cases",
                str(ROOT / "evals" / "cases" / "activation.jsonl"),
                "--output",
                str(output),
                "--variant",
                "with-skill",
                "--system-id",
                "mock-system",
                "--limit",
                "2",
                "--",
                sys.executable,
                str(ROOT / "tests" / "fixtures" / "mock_adapter.py"),
            ]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            results = read_jsonl(output)
            self.assertEqual([result["case_id"] for result in results], ["T01", "T02"])
            self.assertTrue(all(result["variant"] == "with-skill" for result in results))
            self.assertTrue(all(result["system_id"] == "mock-system" for result in results))
            self.assertTrue(all(len(result["configuration_hash"]) == 64 for result in results))

    def test_rejects_adapter_identity_spoofing(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "results.jsonl"
            command = [
                sys.executable,
                str(ROOT / "harness" / "run_adapter.py"),
                "--cases",
                str(ROOT / "evals" / "cases" / "activation.jsonl"),
                "--output",
                str(output),
                "--variant",
                "with-skill",
                "--system-id",
                "spoof-test",
                "--limit",
                "1",
                "--",
                sys.executable,
                str(ROOT / "tests" / "fixtures" / "spoof_adapter.py"),
            ]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("attempted to change run_id", completed.stderr)
            self.assertFalse(output.exists())

    def test_previous_skill_requires_frozen_runtime_path(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "results.jsonl"
            command = [
                sys.executable,
                str(ROOT / "harness" / "run_adapter.py"),
                "--cases",
                str(ROOT / "evals" / "cases" / "activation.jsonl"),
                "--output",
                str(output),
                "--variant",
                "previous-skill",
                "--system-id",
                "baseline-test",
                "--limit",
                "1",
                "--",
                sys.executable,
                str(ROOT / "tests" / "fixtures" / "mock_adapter.py"),
            ]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("--baseline-skill-path is required", completed.stderr)

    def test_rejects_oversized_adapter_output_without_memory_buffering(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "results.jsonl"
            command = [
                sys.executable,
                str(ROOT / "harness" / "run_adapter.py"),
                "--cases",
                str(ROOT / "evals" / "cases" / "activation.jsonl"),
                "--output",
                str(output),
                "--variant",
                "with-skill",
                "--system-id",
                "size-test",
                "--limit",
                "1",
                "--max-output-bytes",
                "10",
                "--",
                sys.executable,
                str(ROOT / "tests" / "fixtures" / "mock_adapter.py"),
            ]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("exceeded --max-output-bytes", completed.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
