import unittest

from scripts.compare_context import compare


class CompareContextTest(unittest.TestCase):
    def test_compares_worktree_with_committed_baseline(self):
        report = compare("HEAD")
        self.assertEqual(report["measurement"], "whitespace-delimited words")
        self.assertEqual(report["byte_measurement"], "UTF-8 source bytes")
        self.assertGreater(report["baseline"]["maximum_standard_route"]["words"], 0)
        self.assertGreater(report["baseline"]["maximum_standard_byte_route"]["bytes"], 0)
        self.assertLess(report["current"]["maximum_standard_route"]["words"], 3001)


if __name__ == "__main__":
    unittest.main()
