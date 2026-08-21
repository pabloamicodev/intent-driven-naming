# Structural Evidence and Rename Plans

Use the strongest repository-native navigation available: code graph, language server, compiler index, AST query, or IDE symbol service. Use literal search separately for strings, configuration, templates, generated sources, and boundary spellings. Never substitute global text replacement for symbol analysis.

Collect only the context needed for the affected symbol: declaration, type, assignments, transformations, callers, consumers, effects, tests, and boundary references. Prefer symbol slices and compact facts over whole-repository source dumps. Do not collect secrets, environment contents, credentials, or unrelated proprietary code in evaluation artifacts.

For a non-trivial refactor, create a rename plan containing:

- the semantic record and evidence;
- selected action and confidence;
- old and proposed spelling;
- symbol identity and affected files;
- protected boundary spellings;
- expected mappings or migrations;
- verification commands and unresolved surfaces.

Validate machine-readable plans with `python scripts/runtime/validate_rename_plan.py PLAN.json` when the runtime script is available. The validator checks protocol consistency; it does not decide whether a name is good.

Apply internal symbols with symbol-aware tooling, inspect literal surfaces, run contract tests before broad tests, and review the final diff for value, control-flow, output-shape, and formatting changes. Stop when domain meaning, dynamic references, generated ownership, or migration authority remains unresolved.
