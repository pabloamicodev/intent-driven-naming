# Structural Evidence and Rename Plans

Use the strongest repository-native navigation available: code graph, language server, compiler index, AST query, or IDE symbol service. Use literal search separately for strings, configuration, templates, generated sources, and boundary spellings. Never substitute global text replacement for symbol analysis.

Collect declaration, types, data flow, callers, consumers, tests, and boundary references only for affected symbols. Prefer symbol slices and compact facts; exclude secrets, environment contents, credentials, and unrelated code from evaluation artifacts.

For a non-trivial refactor, create a rename plan containing:

- semantic record, materiality, evidence, action, and confidence;
- old and proposed spelling, symbol identity, and affected files;
- analysis methods, achieved reference coverage, and dynamic surfaces checked;
- protected spellings, mappings or migrations, and unresolved surfaces;
- maximum authorized changes plus verification, collision, contract, and rollback checks.

Validate machine-readable plans with `python scripts/runtime/validate_rename_plan.py PLAN.json` when the runtime script is available. The validator checks protocol consistency; it does not decide whether a name is good.

Apply with symbol-aware tooling, then inspect literals and run contract checks before broad tests. Do not exceed the change budget. Non-internal changes require complete reference coverage, dynamic changes list checked runtime surfaces, and migrations provide executable rollback. Stop on unresolved meaning, dynamic references, generated ownership, or migration authority.
