import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.capture_environment import version

ROOT = Path(__file__).resolve().parents[1]


class CaptureEnvironmentTest(unittest.TestCase):
    def test_version_reports_none_for_a_missing_tool(self):
        self.assertIsNone(version(["definitely-not-a-real-binary-xyz"]))

    def test_version_reports_output_for_an_installed_tool(self):
        self.assertIn("git", version(["git", "--version"]).lower())

    def test_main_writes_environment_report(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "environment.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "capture_environment.py"),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["schema_version"], "1.0")
            self.assertIn("python", report["tools"])


if __name__ == "__main__":
    unittest.main()
