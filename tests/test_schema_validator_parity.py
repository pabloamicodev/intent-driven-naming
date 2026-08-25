import json
import unittest
from pathlib import Path

from tests._skill_runtime import validate_rename_plan as _validate_rename_plan

ANALYSIS_FIELDS = _validate_rename_plan.ANALYSIS_FIELDS
ANALYSIS_METHODS = _validate_rename_plan.ANALYSIS_METHODS
AUTHORIZATION_FIELDS = _validate_rename_plan.AUTHORIZATION_FIELDS
DECISIONS = _validate_rename_plan.DECISIONS
KINDS = _validate_rename_plan.KINDS
MATERIALITIES = _validate_rename_plan.MATERIALITIES
MEANING_FIELDS = _validate_rename_plan.MEANING_FIELDS
PLAN_FIELDS = _validate_rename_plan.PLAN_FIELDS
RECORD_FIELDS = _validate_rename_plan.RECORD_FIELDS
RISKS = _validate_rename_plan.RISKS
VERIFICATION_FIELDS = _validate_rename_plan.VERIFICATION_FIELDS

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "intent-driven-naming"


class SchemaValidatorParityTest(unittest.TestCase):
    def test_runtime_constants_match_published_schemas(self):
        record_schema = json.loads(
            (SKILL_ROOT / "specification" / "semantic-record.schema.json").read_text(
                encoding="utf-8"
            )
        )
        plan_schema = json.loads(
            (SKILL_ROOT / "specification" / "rename-plan.schema.json").read_text(encoding="utf-8")
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
