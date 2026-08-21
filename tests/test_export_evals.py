import unittest

from scripts.export_evals import build_outputs, parse_activation_cases, parse_behavior_cases


class ExportEvalsTest(unittest.TestCase):
    def test_exports_expected_case_counts(self):
        outputs = build_outputs()
        line_counts = {path.name: len(content.splitlines()) for path, content in outputs.items()}
        self.assertEqual(line_counts["activation.jsonl"], 36)
        self.assertEqual(line_counts["behavior.jsonl"], 34)

    def test_activation_parser_requires_table_rows(self):
        cases = parse_activation_cases(
            "| T01 | Improve function names. | Trigger | Identifier work. |\n"
            "| T02 | Name a product. | Do not trigger | Brand work. |\n"
        )
        self.assertEqual([case["expected_activation"] for case in cases], [True, False])

    def test_behavior_parser_extracts_invariants(self):
        markdown = """# Cases

## B01 — Example

### Prompt

```text
Improve this function.
```

### Required invariants

- Behavior remains unchanged.
- A no-op is acceptable.

## Scoring
"""
        cases = parse_behavior_cases(markdown)
        self.assertEqual(cases[0]["id"], "B01")
        self.assertEqual(len(cases[0]["invariants"]), 2)
        self.assertEqual(cases[0]["invariants"][0]["severity"], "critical")


if __name__ == "__main__":
    unittest.main()
