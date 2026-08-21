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
            self.assertFalse((destination / "evals").exists())

    def test_refuses_to_overwrite_existing_destination(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "intent-driven-naming"
            destination.mkdir()
            with self.assertRaises(ValueError):
                install(destination)


if __name__ == "__main__":
    unittest.main()
