import tempfile
import unittest
from pathlib import Path

from scripts.install_local_skill import default_backup_directory, install, verify_installation


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
            self.assertTrue(backup.parent.samefile(destination.parent / ".skill-backups"))
            self.assertEqual(verify_installation(destination), [])

    def test_default_backup_avoids_one_level_skill_discovery(self):
        destination = Path("agent-home") / "skills" / "intent-driven-naming"
        self.assertEqual(
            default_backup_directory(destination),
            Path("agent-home") / "skill-backups",
        )

    def test_rejects_backup_inside_installation_or_discovery_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            skills = Path(temporary_directory) / "skills"
            destination = skills / "intent-driven-naming"
            destination.mkdir(parents=True)
            (destination / "VERSION").write_text("1.1.0\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inside the installed skill"):
                install(
                    destination,
                    replace=True,
                    backup_directory=destination / "backups",
                )
            with self.assertRaisesRegex(ValueError, "skill discovery directory"):
                install(destination, replace=True, backup_directory=skills)


if __name__ == "__main__":
    unittest.main()
