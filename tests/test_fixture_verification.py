import unittest

from harness.verify_fixtures import verify_fixtures


class FixtureVerificationTest(unittest.TestCase):
    def test_reference_fixtures_pass(self):
        report = verify_fixtures(candidate_root=None, strict_tools=False)
        self.assertTrue(report["valid"])
        self.assertTrue(report["hard_gate_passed"])


if __name__ == "__main__":
    unittest.main()
