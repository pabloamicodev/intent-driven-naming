# Rename-plan validator

`validate_rename_plan.py` checks the portable JSON contract in the sibling
`../specification/rename-plan.schema.json` without third-party packages. It rejects unsafe direct
renames at dynamic, generated, stateful, unknown, and external boundaries; enforces explicit
migration authorization, material wrong-read impact, reference coverage, a bounded change budget,
and verification or rollback evidence for every changing plan.

```console
python skills/intent-driven-naming/scripts/runtime/validate_rename_plan.py path/to/rename-plan.json
```

Use `--json` for machine-readable CI output. The validator checks plan safety; repository-specific
tests, compilation, static analysis, and contract verification must still run separately.
