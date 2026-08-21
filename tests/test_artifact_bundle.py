import tempfile
import unittest
from pathlib import Path

from harness.create_artifact_bundle import build_bundle


class ArtifactBundleTest(unittest.TestCase):
    def test_includes_only_explicit_text_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("value = 1\n", encoding="utf-8")
            (root / "ignored.txt").write_text("ignore\n", encoding="utf-8")
            bundle = build_bundle(root, ["src"], 1000)
            self.assertEqual([item["path"] for item in bundle["files"]], ["src/app.py"])

    def test_rejects_sensitive_looking_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "nested").mkdir()
            (root / "nested" / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_bundle(root, ["nested"], 1000)

    def test_rejects_high_confidence_secret_content_without_echoing_it(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            secret = "sk-abcdefghijklmnopqrstuvwxyz012345"
            (root / "review.txt").write_text(f"token={secret}\n", encoding="utf-8")
            with self.assertRaises(ValueError) as raised:
                build_bundle(root, ["review.txt"], 1000)
            self.assertNotIn(secret, str(raised.exception))
            self.assertIn("exclude or redact", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
