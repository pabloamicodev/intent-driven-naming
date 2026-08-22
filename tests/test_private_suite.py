import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_private_suite import validate_private_suite


class PrivateSuiteTest(unittest.TestCase):
    def test_validates_without_exposing_prompts_in_summary(self):
        case = {
            "schema_version": "1.0",
            "dataset_version": "2.0.0-private.1",
            "id": "T99",
            "suite": "activation",
            "title": "private case",
            "prompt": "confidential prompt",
            "difficulty": "edge",
            "locale": "en",
            "tags": ["private"],
            "expected_activation": True,
            "rationale": "naming-sensitive code task",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.jsonl"
            path.write_text(json.dumps(case) + "\n", encoding="utf-8")
            errors, summary = validate_private_suite([path])
        self.assertEqual(errors, [])
        self.assertEqual(summary["case_count"], 1)
        self.assertNotIn("confidential prompt", json.dumps(summary))


if __name__ == "__main__":
    unittest.main()
