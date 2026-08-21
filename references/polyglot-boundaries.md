# Polyglot Naming Boundaries

Use this protocol when one concept crosses languages, schemas, generated clients, storage, infrastructure, or runtime lookup. The goal is semantic continuity, not identical spelling.

## Build a Boundary Map

Before changing names, record each concept as a compact mapping:

| Concept | Boundary spelling | Internal aliases | Owner | Compatibility rule |
|---|---|---|---|---|
| customer identifier | `customer_id` in JSON | `customerId`, `customer_id` | API schema | preserve wire key |

Include only affected concepts. Mark the authoritative producer, consumers, generated surfaces, persisted state, and dynamic lookups. When ownership or compatibility is unknown, defer the rename.

## Classify Every Spelling

- **Contract:** wire keys, ABI symbols, schema columns, CLI flags, environment keys, routes, resource addresses, reflection strings, registry names, event types, and public parameter labels. Preserve or migrate explicitly.
- **Generated:** code produced from a schema or generator. Change the source and regenerate; do not patch the output.
- **Mapped:** internal aliases intentionally differ from the boundary. Keep an explicit serializer, annotation, adapter, or translation.
- **Internal:** implementation-only identifiers proven not to escape. Rename with the native symbol-aware tooling.

Do not infer that a local declaration is internal merely because its scope is small. Shorthand properties, macros, decorators, named arguments, templates, reflection, and code generation can expose its spelling.

## Choose One of Five Actions

For every affected name choose and state one action:

1. `keep` when it is clear or contract-bound.
2. `rename` when it is internal and the new semantic payload is better.
3. `map` when internal clarity can improve while the boundary remains stable.
4. `migrate` when the external spelling must change through a versioned compatibility plan.
5. `defer` when ownership, meaning, or consumers cannot be established safely.

Never hide a migration inside a cosmetic rename.

## Keep the Change Atomic

Use one domain vocabulary map across the task, then render it idiomatically per ecosystem. Update producer, adapters, consumers, tests, documentation, and migration metadata as one reviewed unit when the contract changes. For persisted or deployed identifiers, include rollback and forward-compatibility steps.

Generated boundaries follow this order:

1. change the authoritative schema or generator;
2. regenerate with the pinned toolchain;
3. review the generated diff;
4. compile or validate every affected consumer;
5. verify old and new compatibility when migration is intentional.

## Verification Matrix

Verify each changed surface with its own authoritative tool. At minimum check:

- compilation or static analysis for every actively changed language;
- serialization or protocol compatibility for boundary mappings;
- registry, reflection, template, or dependency-injection lookup behavior;
- persisted state moves for database or infrastructure identifiers;
- generated output reproducibility when a generator is involved;
- repository-wide residual references using syntax-aware search where possible.

A passing test in one ecosystem does not prove a cross-language rename safe. Report any unverified consumer as residual risk.
