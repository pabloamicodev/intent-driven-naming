# Rename-plan validator

`validate_rename_plan.py` checks the portable JSON contract in
`specification/rename-plan.schema.json` without third-party packages. It rejects unsafe direct
renames at dynamic, generated, stateful, unknown, and external boundaries; enforces explicit
migration authorization; and requires verification evidence for every changing plan.

```console
python scripts/runtime/validate_rename_plan.py path/to/rename-plan.json
```

Use `--json` for machine-readable CI output. The validator checks plan safety; repository-specific
tests, compilation, static analysis, and contract verification must still run separately.
