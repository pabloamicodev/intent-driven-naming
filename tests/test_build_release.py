import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build_release import build


class BuildReleaseTest(unittest.TestCase):
    def test_build_is_reproducible_and_runtime_only(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_artifacts = build(Path(first))
            second_artifacts = build(Path(second))
            first_hash = hashlib.sha256(first_artifacts["archive"].read_bytes()).hexdigest()
            second_hash = hashlib.sha256(second_artifacts["archive"].read_bytes()).hexdigest()
            self.assertEqual(first_hash, second_hash)
            with zipfile.ZipFile(first_artifacts["archive"]) as archive:
                names = archive.namelist()
                manifest = json.loads(
                    archive.read("intent-driven-naming/PACKAGE-MANIFEST.json")
                )
            self.assertIn("intent-driven-naming/SKILL.md", names)
            self.assertIn("intent-driven-naming/scripts/runtime/validate_rename_plan.py", names)
            self.assertEqual(manifest["skill"], "intent-driven-naming")
            self.assertIn("SKILL.md", manifest["files"])
            with zipfile.ZipFile(first_artifacts["archive"]) as archive:
                for relative, expected_digest in manifest["files"].items():
                    content = archive.read(f"intent-driven-naming/{relative}")
                    self.assertEqual(hashlib.sha256(content).hexdigest(), expected_digest)
            self.assertFalse(any("evals/" in name for name in names))


if __name__ == "__main__":
    unittest.main()
