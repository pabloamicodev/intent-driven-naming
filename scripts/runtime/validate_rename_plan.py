#!/usr/bin/env python3
"""Validate an Intent-Driven Naming 2.0 rename plan without dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PLAN_FIELDS = {
    "schema_version", "plan_id", "scope", "authorization", "analysis", "records", "verification",
}
AUTHORIZATION_FIELDS = {"mode", "migration_authorized", "maximum_changed_symbols"}
ANALYSIS_FIELDS = {"methods", "reference_coverage", "dynamic_surfaces_checked"}
VERIFICATION_FIELDS = {
    "commands", "contract_checks", "collision_checks", "rollback_commands",
}
RECORD_FIELDS = {
    "symbol_id", "identifier", "symbol_kind", "location", "meaning", "evidence",
    "wrong_read", "materiality", "decision", "proposed_name", "confidence", "contract_risk",
    "protected_spellings", "unresolved_surfaces",
}
MEANING_FIELDS = {
    "concept", "role", "state", "representation", "cardinality", "unit_or_basis",
    "ownership_or_trust", "effect", "scope",
}
KINDS = {
    "callable", "parameter", "local", "field", "property", "type", "type-parameter",
    "constant", "enum", "variant", "module", "package", "namespace", "event", "message",
    "query", "schema", "infrastructure", "other",
}
DECISIONS = {"keep", "rename", "map", "migrate", "defer"}
RISKS = {"internal", "cross-module", "external", "dynamic", "generated", "stateful", "unknown"}
MATERIALITIES = {"none", "low", "material", "critical"}
ANALYSIS_METHODS = {
    "symbol-graph", "language-server", "compiler-index", "ast", "text-search", "manual",
}
UNSAFE_DIRECT_RENAME_RISKS = {"external", "dynamic", "generated", "stateful", "unknown"}
CHANGING_DECISIONS = {"rename", "map", "migrate"}


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(_string(item) for item in value)
        and len(value) == len(set(value))
    )


def validate_plan(plan: Any) -> tuple[list[str], list[str]]:
    """Return deterministic errors and warnings for a decoded rename plan."""
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(plan, dict):
        return ["plan must be a JSON object"], warnings
    unknown = set(plan) - PLAN_FIELDS
    if unknown:
        errors.append(f"plan has unknown fields: {', '.join(sorted(unknown))}")
    missing = PLAN_FIELDS - set(plan)
    if missing:
        errors.append(f"plan is missing fields: {', '.join(sorted(missing))}")
    if plan.get("schema_version") != "2.0":
        errors.append("schema_version must be 2.0")
    plan_id = plan.get("plan_id")
    if not _string(plan_id) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,127}", plan_id):
        errors.append("plan_id must be 3-128 lowercase letters, digits, dots, underscores, or hyphens")
    if not _string_list(plan.get("scope"), nonempty=True):
        errors.append("scope must be a non-empty unique string array")

    authorization = plan.get("authorization")
    if not isinstance(authorization, dict) or set(authorization) != AUTHORIZATION_FIELDS:
        errors.append(
            "authorization must contain only mode, migration_authorized, and maximum_changed_symbols"
        )
        mode, migration_authorized, maximum_changed_symbols = None, False, None
    else:
        mode = authorization.get("mode")
        migration_authorized = authorization.get("migration_authorized")
        maximum_changed_symbols = authorization.get("maximum_changed_symbols")
        if mode not in {"refactor", "migration"}:
            errors.append("authorization.mode must be refactor or migration")
        if not isinstance(migration_authorized, bool):
            errors.append("authorization.migration_authorized must be boolean")
            migration_authorized = False
        if mode == "refactor" and migration_authorized:
            errors.append("refactor mode cannot authorize migration")
        if (
            isinstance(maximum_changed_symbols, bool)
            or not isinstance(maximum_changed_symbols, int)
            or not 0 <= maximum_changed_symbols <= 500
        ):
            errors.append("authorization.maximum_changed_symbols must be an integer from 0 to 500")
            maximum_changed_symbols = None

    analysis = plan.get("analysis")
    if not isinstance(analysis, dict) or set(analysis) != ANALYSIS_FIELDS:
        errors.append(
            "analysis must contain only methods, reference_coverage, and dynamic_surfaces_checked"
        )
        methods, reference_coverage, dynamic_surfaces_checked = [], None, []
    else:
        methods = analysis.get("methods")
        reference_coverage = analysis.get("reference_coverage")
        dynamic_surfaces_checked = analysis.get("dynamic_surfaces_checked")
        if (
            not isinstance(methods, list)
            or not methods
            or any(not isinstance(method, str) or method not in ANALYSIS_METHODS for method in methods)
            or len(methods) != len(set(methods))
        ):
            errors.append("analysis.methods must be a non-empty unique array of documented methods")
            methods = []
        if reference_coverage not in {"complete", "partial", "unknown"}:
            errors.append("analysis.reference_coverage must be complete, partial, or unknown")
        if not _string_list(dynamic_surfaces_checked):
            errors.append("analysis.dynamic_surfaces_checked must be a unique string array")
            dynamic_surfaces_checked = []

    records = plan.get("records")
    if not isinstance(records, list) or not 1 <= len(records) <= 500:
        errors.append("records must contain 1-500 semantic records")
        records = []
    symbol_ids: set[str] = set()
    locations: set[tuple[str, str]] = set()
    changed_records: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        unknown_record = set(record) - RECORD_FIELDS
        missing_record = RECORD_FIELDS - set(record)
        if unknown_record:
            errors.append(f"{prefix} has unknown fields: {', '.join(sorted(unknown_record))}")
        if missing_record:
            errors.append(f"{prefix} is missing fields: {', '.join(sorted(missing_record))}")
        for field in ("symbol_id", "identifier", "location"):
            if not _string(record.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
        symbol_id = record.get("symbol_id")
        if _string(symbol_id):
            if symbol_id in symbol_ids:
                errors.append(f"{prefix}.symbol_id duplicates {symbol_id}")
            symbol_ids.add(symbol_id)
        identity = (str(record.get("location")), str(record.get("identifier")))
        if identity in locations:
            errors.append(f"{prefix} duplicates symbol location and identifier {identity!r}")
        locations.add(identity)
        if record.get("symbol_kind") not in KINDS:
            errors.append(f"{prefix}.symbol_kind is invalid")
        meaning = record.get("meaning")
        if not isinstance(meaning, dict) or set(meaning) - MEANING_FIELDS or "concept" not in meaning:
            errors.append(f"{prefix}.meaning must contain concept and only documented dimensions")
        elif not _string(meaning.get("concept")):
            errors.append(f"{prefix}.meaning.concept must be a non-empty string")
        elif any(value is not None and not _string(value) for value in meaning.values()):
            errors.append(f"{prefix}.meaning values must be non-empty strings or null")
        evidence = record.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}.evidence must be a non-empty array")
        else:
            for evidence_index, item in enumerate(evidence):
                if (
                    not isinstance(item, dict)
                    or set(item) != {"source", "fact"}
                    or not _string(item.get("source"))
                    or not _string(item.get("fact"))
                ):
                    errors.append(f"{prefix}.evidence[{evidence_index}] must contain source and fact")
        decision = record.get("decision")
        materiality = record.get("materiality")
        risk = record.get("contract_risk")
        proposed = record.get("proposed_name")
        wrong_read = record.get("wrong_read")
        protected = record.get("protected_spellings")
        unresolved = record.get("unresolved_surfaces")
        if decision not in DECISIONS:
            errors.append(f"{prefix}.decision is invalid")
        if materiality not in MATERIALITIES:
            errors.append(f"{prefix}.materiality is invalid")
        if risk not in RISKS:
            errors.append(f"{prefix}.contract_risk is invalid")
        if record.get("confidence") not in {"high", "medium", "low"}:
            errors.append(f"{prefix}.confidence is invalid")
        if wrong_read is not None and not _string(wrong_read):
            errors.append(f"{prefix}.wrong_read must be a non-empty string or null")
        if not _string_list(protected):
            errors.append(f"{prefix}.protected_spellings must be a unique string array")
        if not _string_list(unresolved):
            errors.append(f"{prefix}.unresolved_surfaces must be a unique string array")
        if decision in CHANGING_DECISIONS:
            changed_records.append(record)
            if not _string(proposed):
                errors.append(f"{prefix}.proposed_name is required for {decision}")
            elif proposed == record.get("identifier"):
                errors.append(f"{prefix}.proposed_name must differ from identifier")
            if not _string(wrong_read):
                errors.append(f"{prefix}.wrong_read is required for {decision}")
            if materiality not in {"material", "critical"}:
                errors.append(f"{prefix}.{decision} requires material or critical impact")
        elif decision in {"keep", "defer"} and proposed is not None:
            errors.append(f"{prefix}.proposed_name must be null for {decision}")
        if decision == "map" and not protected:
            errors.append(f"{prefix}.map requires at least one protected spelling")
        if decision == "migrate" and not (mode == "migration" and migration_authorized is True):
            errors.append(f"{prefix}.migrate requires explicitly authorized migration mode")
        if decision == "rename" and risk in UNSAFE_DIRECT_RENAME_RISKS:
            errors.append(f"{prefix}.rename is unsafe for {risk} risk; use map, migrate, or defer")
        if decision in CHANGING_DECISIONS and risk == "unknown":
            errors.append(f"{prefix} cannot change while contract risk is unknown")
        if decision in CHANGING_DECISIONS and unresolved:
            errors.append(f"{prefix} cannot change while unresolved contract surfaces remain")
        if record.get("confidence") == "low" and decision in CHANGING_DECISIONS:
            errors.append(f"{prefix} cannot change a low-confidence symbol; use defer or keep")

    if (
        maximum_changed_symbols is not None
        and len(changed_records) > maximum_changed_symbols
    ):
        errors.append(
            f"plan changes {len(changed_records)} symbols but authorization allows "
            f"{maximum_changed_symbols}"
        )
    non_internal_changes = [
        record for record in changed_records if record.get("contract_risk") != "internal"
    ]
    if non_internal_changes and reference_coverage != "complete":
        errors.append("non-internal changes require complete reference coverage")
    if (
        any(record.get("contract_risk") == "dynamic" for record in changed_records)
        and not dynamic_surfaces_checked
    ):
        errors.append("dynamic changes require at least one checked dynamic surface")

    verification = plan.get("verification")
    if not isinstance(verification, dict) or set(verification) != VERIFICATION_FIELDS:
        errors.append(
            "verification must contain only commands, contract_checks, collision_checks, "
            "and rollback_commands"
        )
    else:
        commands = verification.get("commands")
        checks = verification.get("contract_checks")
        collision_checks = verification.get("collision_checks")
        rollback_commands = verification.get("rollback_commands")
        if not _string_list(commands):
            errors.append("verification.commands must be a unique string array")
        if not _string_list(checks):
            errors.append("verification.contract_checks must be a unique string array")
        if not _string_list(collision_checks):
            errors.append("verification.collision_checks must be a unique string array")
        if not _string_list(rollback_commands):
            errors.append("verification.rollback_commands must be a unique string array")
        if changed_records and not commands:
            errors.append("a changing plan requires at least one verification command")
        if changed_records and not collision_checks:
            errors.append("a changing plan requires at least one collision check")
        if non_internal_changes and not checks:
            errors.append("non-internal changes require at least one contract check")
        if any(record.get("decision") == "migrate" for record in changed_records) and not rollback_commands:
            errors.append("migration requires at least one rollback command")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors, warnings = [f"cannot read plan: {exc}"], []
    else:
        errors, warnings = validate_plan(plan)
    if args.json_output:
        print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings}, indent=2))
    else:
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
        if errors:
            print("\n".join(f"error: {error}" for error in errors), file=sys.stderr)
        else:
            print(f"valid rename plan: {args.plan}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
