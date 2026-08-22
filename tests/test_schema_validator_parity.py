import json
import unittest
from pathlib import Path

from scripts.runtime.validate_rename_plan import (
    ANALYSIS_FIELDS,
    ANALYSIS_METHODS,
    AUTHORIZATION_FIELDS,
    DECISIONS,
    KINDS,
    MATERIALITIES,
    MEANING_FIELDS,
    PLAN_FIELDS,
    RECORD_FIELDS,
    RISKS,
    VERIFICATION_FIELDS,
)

ROOT = Path(__file__).resolve().parents[1]


class SchemaValidatorParityTest(unittest.TestCase):
    def test_runtime_constants_match_published_schemas(self):
        record_schema = json.loads(
            (ROOT / "specification" / "semantic-record.schema.json").read_text(encoding="utf-8")
        )
        plan_schema = json.loads(
            (ROOT / "specification" / "rename-plan.schema.json").read_text(encoding="utf-8")
        )
        record_properties = record_schema["properties"]
        plan_properties = plan_schema["properties"]

        self.assertEqual(RECORD_FIELDS, set(record_properties))
        self.assertEqual(RECORD_FIELDS, set(record_schema["required"]))
        self.assertEqual(PLAN_FIELDS, set(plan_properties))
        self.assertEqual(PLAN_FIELDS, set(plan_schema["required"]))
        self.assertEqual(
            AUTHORIZATION_FIELDS,
            set(plan_properties["authorization"]["properties"]),
        )
        self.assertEqual(ANALYSIS_FIELDS, set(plan_properties["analysis"]["properties"]))
        self.assertEqual(
            VERIFICATION_FIELDS,
            set(plan_properties["verification"]["properties"]),
        )
        self.assertEqual(MEANING_FIELDS, set(record_properties["meaning"]["properties"]))
        self.assertEqual(KINDS, set(record_properties["symbol_kind"]["enum"]))
        self.assertEqual(DECISIONS, set(record_properties["decision"]["enum"]))
        self.assertEqual(MATERIALITIES, set(record_properties["materiality"]["enum"]))
        self.assertEqual(RISKS, set(record_properties["contract_risk"]["enum"]))
        methods = plan_properties["analysis"]["properties"]["methods"]["items"]["enum"]
        self.assertEqual(ANALYSIS_METHODS, set(methods))


if __name__ == "__main__":
    unittest.main()
