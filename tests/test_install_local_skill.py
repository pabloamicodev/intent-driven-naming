import tempfile
import unittest
from pathlib import Path

from scripts.install_local_skill import install, verify_installation


class InstallLocalSkillTest(unittest.TestCase):
    def test_installs_only_runtime_surface_and_verifies_hashes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "intent-driven-naming"
            install(destination)
            self.assertEqual(verify_installation(destination), [])
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertTrue((destination / "references" / "naming-model.md").is_file())
            self.assertTrue((destination / "scripts" / "runtime" / "validate_rename_plan.py").is_file())
            self.assertTrue((destination / "specification" / "rename-plan.schema.json").is_file())
            self.assertTrue((destination / "LICENSE").is_file())
            self.assertFalse((destination / "evals").exists())

    def test_refuses_to_overwrite_existing_destination(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "intent-driven-naming"
            destination.mkdir()
            with self.assertRaises(ValueError):
                install(destination)

    def test_replaces_atomically_and_retains_backup(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "intent-driven-naming"
            destination.mkdir()
            (destination / "VERSION").write_text("1.1.0\n", encoding="utf-8")
            backup = install(destination, replace=True)
            self.assertIsNotNone(backup)
            self.assertTrue((backup / "VERSION").is_file())
            self.assertEqual(verify_installation(destination), [])


if __name__ == "__main__":
    unittest.main()
