import json
import unittest
from pathlib import Path

from harness.routing import allowed_behavior_resources, loaded_profile_count

ROOT = Path(__file__).resolve().parents[1]


class RoutingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = json.loads(
            (ROOT / "specification" / "routes.json").read_text(encoding="utf-8")
        )

    def test_routes_only_applicable_mode_features_and_profile(self):
        case = {
            "mode": "generation",
            "languages": ["python"],
            "contract_risk": "internal",
            "features": ["high-risk"],
            "tags": ["callable"],
        }
        allowed = allowed_behavior_resources(case, self.routes)
        self.assertIn("references/new-code-workflow.md", allowed)
        self.assertIn("references/dynamic-languages.md", allowed)
        self.assertIn("references/high-risk-semantics.md", allowed)
        self.assertIn("references/callable-naming.md", allowed)
        self.assertNotIn("references/systems-languages.md", allowed)

    def test_web_profile_counts_as_one_family(self):
        resources = {
            "references/typescript-javascript.md",
            "references/web-frameworks.md",
        }
        self.assertEqual(loaded_profile_count(resources, self.routes), 1)

    def test_declaration_guidance_loads_only_when_declared(self):
        case = {
            "mode": "generation",
            "languages": ["go"],
            "contract_risk": "internal",
            "features": ["declaration"],
            "tags": [],
        }
        allowed = allowed_behavior_resources(case, self.routes)
        self.assertIn("references/declaration-naming.md", allowed)
        self.assertNotIn("references/callable-naming.md", allowed)
        self.assertNotIn("references/local-variable-naming.md", allowed)

    def test_unlisted_language_routes_convention_discovery_without_a_fake_profile(self):
        case = {
            "mode": "audit",
            "languages": ["lua"],
            "contract_risk": "internal",
            "tags": [],
        }
        allowed = allowed_behavior_resources(case, self.routes)
        self.assertIn("references/language-conventions.md", allowed)
        self.assertNotIn("references/dynamic-languages.md", allowed)


if __name__ == "__main__":
    unittest.main()
