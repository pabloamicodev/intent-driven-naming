import json
import unittest

from scripts.export_evals import build_outputs, parse_activation_cases, parse_behavior_cases


class ExportEvalsTest(unittest.TestCase):
    def test_exports_versioned_cases_and_manifest(self):
        outputs = build_outputs()
        by_name = {path.name: content for path, content in outputs.items()}
        self.assertEqual(len(by_name["activation.jsonl"].splitlines()), 84)
        self.assertEqual(len(by_name["behavior.jsonl"].splitlines()), 52)
        manifest = json.loads(by_name["manifest.json"])
        self.assertEqual(manifest["dataset_version"], "2.0.0")
        self.assertEqual(manifest["counts"]["activation"], 84)
        self.assertEqual(manifest["counts"]["behavior"], 52)
        self.assertEqual(manifest["counts"]["invariants"], 202)

    def test_activation_parser_requires_explicit_strata(self):
        cases = parse_activation_cases(
            "| T01 | Improve function names. | Trigger | standard | en | Identifier work. |\n"
            "| T02 | Name a product. | Do not trigger | adversarial | es | Brand work. |\n",
            "2.0.0",
        )
        self.assertEqual([case["expected_activation"] for case in cases], [True, False])
        self.assertEqual(cases[1]["difficulty"], "adversarial")
        self.assertEqual(cases[1]["locale"], "es")

    def test_behavior_parser_extracts_explicit_metadata_and_invariants(self):
        markdown = """# Cases

## B01 — Example

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: typescript, python
- Contract risk: external
- Expected decisions: map

### Prompt

```text
Improve this function.
```

### Required invariants

- [critical][semantic] Behavior remains unchanged.
- [major][human] A no-op is acceptable.

## Scoring
"""
        cases = parse_behavior_cases(markdown, "2.0.0")
        self.assertEqual(cases[0]["id"], "B01")
        self.assertEqual(cases[0]["languages"], ["typescript", "python"])
        self.assertEqual(cases[0]["expected_decisions"], ["map"])
        self.assertEqual(cases[0]["invariants"][0]["severity"], "critical")
        self.assertEqual(cases[0]["invariants"][1]["grading"], "human")


if __name__ == "__main__":
    unittest.main()
