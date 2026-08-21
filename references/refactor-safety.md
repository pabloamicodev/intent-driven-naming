# Behavior-Preserving Rename Safety

A naming refactor authorizes identifier changes in the requested scope. It does not authorize architecture redesign, migrations, dependencies, control-flow changes, or broad formatting.

## Inventory Before Editing

For each selected symbol identify its definition, references, imports, exports, aliases, callers, implementations, overrides, paired identifiers, tests, strings, captures, patterns, generated owners, and protected spellings. Use structural navigation for symbols and literal search for runtime or serialized names.

Treat these as contracts unless migration is explicitly authorized:

- public APIs, parameters usable by name, package exports, and SDK surfaces;
- serialized fields, schemas, database objects, routes, forms, configuration, and environment keys;
- events, topics, metric dimensions, reflection strings, registries, dependency-injection tokens, templates, and selectors;
- protocol, trait, interface, override, framework, ABI, FFI, and generated names;
- CLI names, infrastructure addresses, state identifiers, remote resource names, and automation inputs.

Use `map` when an internal alias can improve while a boundary remains stable. Change generated sources or generators, not generated output.

## Apply a Controlled Plan

1. Confirm the action, proposed spelling, evidence, affected symbols, and protected boundaries.
2. Rename definitions and symbol references with native tooling.
3. Update the smallest necessary semantic family.
4. Inspect literals, shorthand output, destructuring, named calls, shadowing, captures, macros, and templates separately.
5. Preserve output keys explicitly when a local spelling changes.
6. Format only touched code required by the rename.

For public or cross-module symbols, repository search does not prove that external consumers do not exist. Use compatibility aliases or a versioned migration only when authorized.

## Verify in Risk Order

1. Serialized shapes, public calls, dynamic lookup, generated reproducibility, and persisted or deployed identity.
2. Targeted behavioral tests.
3. Type checking, compilation, linting, and static analysis.
4. Broader repository, schema, query, or infrastructure checks.
5. Final diff review for value, control-flow, output, and unrelated formatting changes.

Stop and report unresolved risk when meaning is ambiguous, dynamic references cannot be traced, generated ownership is missing, the change becomes a migration, scope expands materially, or verification finds unexplained behavior differences.

Report rename groups, protected spellings, commands and results, and any unverified surface. Never claim preservation from a successful textual replacement alone.
