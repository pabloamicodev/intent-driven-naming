import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.eval_core import read_jsonl


ROOT = Path(__file__).resolve().parents[1]


class CodexAdapterTest(unittest.TestCase):
    def test_reference_adapter_isolates_and_reports_runtime_skill(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            records_by_variant = {}
            for variant in ("with-skill", "without-skill"):
                output = temporary / f"{variant}.jsonl"
                command = [
                    sys.executable, str(ROOT / "harness" / "run_adapter.py"),
                    "--cases", str(ROOT / "evals" / "cases" / "activation.jsonl"),
                    "--output", str(output), "--variant", variant,
                    "--system-id", "fake-codex", "--limit", "1", "--",
                    sys.executable, str(ROOT / "adapters" / "codex_cli.py"),
                    "--codex", sys.executable,
                    "--codex-prefix-arg", str(ROOT / "tests" / "fixtures" / "fake_codex.py"),
                    "--model", "fake-model", "--model-version", "fake-version",
                    "--artifact-output-root", str(temporary / "artifacts"),
                ]
                subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
                records_by_variant[variant] = read_jsonl(output)[0]
            self.assertTrue(records_by_variant["with-skill"]["selected_skill"])
            self.assertFalse(records_by_variant["without-skill"]["selected_skill"])
            self.assertEqual(records_by_variant["without-skill"]["loaded_resources"], [])
            self.assertEqual(records_by_variant["with-skill"]["implementation"]["agent"], "codex-cli")
            self.assertIn(
                "references/naming-model.md",
                records_by_variant["with-skill"]["loaded_resources"],
            )


if __name__ == "__main__":
    unittest.main()
