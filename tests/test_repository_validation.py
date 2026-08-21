import unittest

from scripts.validate_repository import validate_repository


class RepositoryValidationTest(unittest.TestCase):
    def test_repository_conforms(self):
        report = validate_repository()
        self.assertTrue(report["valid"], "\n".join(report["errors"]))


if __name__ == "__main__":
    unittest.main()
