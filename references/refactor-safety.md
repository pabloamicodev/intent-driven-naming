# Behavior-Preserving Rename Safety

A naming refactor authorizes identifiers in scope, not architecture, dependencies, control flow, formatting churn, or an undeclared migration.

## Inventory Before Editing

For each selected symbol find its definition, references, aliases, callers, implementations, overrides, semantic family, tests, strings, captures, generated owner, and protected spellings. Use structural navigation for symbols and literal search for runtime names.

Treat public/named parameters, exports, schemas, serialized or database fields, routes, configuration, environment keys, events, topics, metrics, reflection, registries, protocols, overrides, framework hooks, ABI/FFI, generated names, CLI names, infrastructure addresses, persisted state, and automation inputs as contracts. Map to an internal alias when the boundary stays fixed; edit generators rather than generated output.

## Apply a Controlled Plan

1. Freeze the action, target, evidence, affected symbols, change budget, and protected boundaries.
2. Rename definitions/references with native tooling and update the smallest coherent family.
3. Inspect literals, shorthand output, destructuring, named calls, shadowing, captures, macros, and templates separately.
4. Preserve output keys explicitly and format only touched code.

Repository search cannot prove public consumers do not exist. Use compatibility or migration only when authorized.

Verify contracts and dynamic lookup first, then targeted behavior, type/compile/static checks, broader integration checks, and a final diff review for value, control flow, output, and unrelated churn. Stop on ambiguous meaning, unresolved dynamic references, missing generated ownership, migration scope, or unexplained behavior differences. Report groups, protected spellings, checks, and unverified surfaces; textual replacement alone proves nothing.
