# Structural Evidence and Rename Plans

Use the strongest repository-native navigation: code graph, language server, compiler index, AST query, or IDE symbol service. Literal search separately covers strings, configuration, templates, generated sources, and boundary spellings. Never substitute global text replacement for symbol analysis.

## Acquire Evidence Progressively

1. Read the declaration, type/signature, enclosing scope, and local vocabulary.
2. If meaning remains ambiguous, inspect assignments, branches, reads, sinks, and focused tests.
3. If a change appears material, inspect callers, consumers, overrides, aliases, and its semantic family.
4. Only for a changing, dynamic, generated, stateful, or external symbol, expand to complete affected-reference and boundary coverage.

Stop when evidence supports `keep`, or uncertainty requires `defer`. Do not scan or transmit an entire repository for one name. Retain compact facts and locations, not code copies; exclude secrets, environment values, credentials, histories, and unrelated source.

For a non-trivial refactor, record semantic decisions, symbol identities and affected files, analysis methods and coverage, protected/unresolved surfaces, change budget, and verification, collision, contract, and rollback checks.

Validate a machine-readable plan with `python scripts/runtime/validate_rename_plan.py PLAN.json` when available. The validator checks protocol consistency, not name quality. Apply with symbol-aware tooling, inspect literals, and stop when scope, ownership, or required coverage is unresolved.
