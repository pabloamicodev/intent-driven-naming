import unittest

from scripts.runtime.validate_rename_plan import validate_plan


def record(**overrides):
    value = {
        "symbol_id": "src/orders.py:12:total",
        "identifier": "total",
        "symbol_kind": "local",
        "location": "src/orders.py:12",
        "meaning": {"concept": "paid invoice total", "unit_or_basis": "cents"},
        "evidence": [{"source": "assignment", "fact": "sums amount_in_cents for paid invoices"}],
        "wrong_read": "could be read as a count or a total in major currency units",
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
        "authorization": {"mode": "refactor", "migration_authorized": False, **authorization},
        "records": [item or record()],
        "verification": {"commands": ["python -m unittest"], "contract_checks": []},
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
        errors, _ = validate_plan(plan(migrating))
        self.assertIn("requires explicitly authorized migration mode", "\n".join(errors))

    def test_rejects_change_with_unresolved_surface(self):
        errors, _ = validate_plan(plan(record(unresolved_surfaces=["reflection lookup"])))
        self.assertIn("unresolved contract surfaces", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
