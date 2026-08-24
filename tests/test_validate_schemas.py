import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ValidateSchemasTest(unittest.TestCase):
    def test_validates_current_repository_schemas_and_writes_json_output(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            json_output = Path(temporary_directory) / "report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_schemas.py"),
                    "--json-output",
                    str(json_output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(json_output.read_text(encoding="utf-8"))
            self.assertTrue(report["valid"])
            self.assertGreater(report["schemas"], 0)
            self.assertGreater(report["cases"], 0)


if __name__ == "__main__":
    unittest.main()
