import unittest

from tests._skill_runtime import validate_rename_plan as _validate_rename_plan

validate_plan = _validate_rename_plan.validate_plan


def record(**overrides):
    value = {
        "symbol_id": "src/orders.py:12:total",
        "identifier": "total",
        "symbol_kind": "local",
        "location": "src/orders.py:12",
        "meaning": {"concept": "paid invoice total", "unit_or_basis": "cents"},
        "evidence": [{"source": "assignment", "fact": "sums amount_in_cents for paid invoices"}],
        "wrong_read": "could be read as a count or a total in major currency units",
        "materiality": "material",
        "decision": "rename",
        "proposed_name": "paid_invoice_total_cents",
        "confidence": "high",
        "contract_risk": "internal",
        "protected_spellings": [],
        "unresolved_surfaces": [],
    }
    value.update(overrides)
    return value


def plan(item=None, **authorization):
    return {
        "schema_version": "2.0",
        "plan_id": "orders-local-rename",
        "scope": ["src/orders.py"],
        "authorization": {
            "mode": "refactor",
            "migration_authorized": False,
            "maximum_changed_symbols": 1,
            **authorization,
        },
        "analysis": {
            "methods": ["ast", "text-search"],
            "reference_coverage": "complete",
            "dynamic_surfaces_checked": [],
        },
        "records": [item or record()],
        "verification": {
            "commands": ["python -m unittest"],
            "contract_checks": [],
            "collision_checks": ["symbol table has no proposed-name collision"],
            "rollback_commands": [],
        },
    }


class RenamePlanTest(unittest.TestCase):
    def test_accepts_internal_verified_rename(self):
        self.assertEqual(validate_plan(plan()), ([], []))

    def test_rejects_direct_external_rename(self):
        value = plan(record(contract_risk="external"))
        value["verification"]["contract_checks"] = ["external spelling remains stable"]
        errors, _ = validate_plan(value)
        self.assertIn("unsafe for external risk", "\n".join(errors))

    def test_map_preserves_contract_spelling(self):
        mapped = record(
            decision="map",
            contract_risk="external",
            protected_spellings=["customerId"],
        )
        value = plan(mapped)
        value["verification"]["contract_checks"] = ["serialized key remains customerId"]
        self.assertEqual(validate_plan(value), ([], []))

    def test_migration_requires_explicit_authorization(self):
        migrating = record(decision="migrate", contract_risk="stateful")
        value = plan(migrating)
        value["verification"]["contract_checks"] = ["state identity migration is explicit"]
        value["verification"]["rollback_commands"] = ["terraform state mv new old"]
        errors, _ = validate_plan(value)
        self.assertIn("requires explicitly authorized migration mode", "\n".join(errors))

    def test_rejects_change_with_unresolved_surface(self):
        errors, _ = validate_plan(plan(record(unresolved_surfaces=["reflection lookup"])))
        self.assertIn("unresolved contract surfaces", "\n".join(errors))

    def test_rejects_cosmetic_churn_and_unchanged_proposal(self):
        errors, _ = validate_plan(plan(record(materiality="low", proposed_name="total")))
        rendered = "\n".join(errors)
        self.assertIn("must differ from identifier", rendered)
        self.assertIn("requires material or critical impact", rendered)

    def test_rejects_low_confidence_change(self):
        errors, _ = validate_plan(plan(record(confidence="low")))
        self.assertIn("cannot change a low-confidence symbol", "\n".join(errors))

    def test_enforces_authorized_change_budget(self):
        value = plan()
        value["authorization"]["maximum_changed_symbols"] = 0
        errors, _ = validate_plan(value)
        self.assertIn("authorization allows 0", "\n".join(errors))

    def test_changing_plan_requires_collision_evidence(self):
        value = plan()
        value["verification"]["collision_checks"] = []
        errors, _ = validate_plan(value)
        self.assertIn("collision check", "\n".join(errors))

    def test_non_internal_change_requires_complete_coverage(self):
        mapped = record(
            decision="map",
            contract_risk="external",
            protected_spellings=["customerId"],
        )
        value = plan(mapped)
        value["analysis"]["reference_coverage"] = "partial"
        value["verification"]["contract_checks"] = ["serialized key remains customerId"]
        errors, _ = validate_plan(value)
        self.assertIn("complete reference coverage", "\n".join(errors))

    def test_dynamic_change_requires_checked_runtime_surface(self):
        mapped = record(
            decision="map",
            contract_risk="dynamic",
            protected_spellings=["legacy_handler"],
        )
        value = plan(mapped)
        value["verification"]["contract_checks"] = ["registry key remains legacy_handler"]
        errors, _ = validate_plan(value)
        self.assertIn("checked dynamic surface", "\n".join(errors))

    def test_malformed_analysis_returns_errors_instead_of_crashing(self):
        value = plan()
        value["analysis"]["methods"] = [["ast"]]
        errors, _ = validate_plan(value)
        self.assertIn("documented methods", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
