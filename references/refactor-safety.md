# Behavior-Preserving Rename Safety

Use this protocol after a naming audit identifies supported renames and the user has authorized edits.

## Preserve the Authorization Boundary

A naming refactor authorizes identifier changes in the requested scope. It does not authorize architecture changes, data migrations, public API redesign, dependency upgrades, or unrelated cleanup.

If the requested rename implies a contract migration, separate that work and obtain explicit direction before proceeding.

## Inventory the Rename Surface

For every symbol selected for change, identify:

- its definition;
- direct and indirect references;
- imports, exports, aliases, overrides, and implementations;
- paired or derived identifiers that would become inconsistent;
- tests, fixtures, snapshots, comments, and documentation that refer to the code concept;
- string-based or runtime references;
- boundaries where the old spelling must remain.

Prefer symbol-aware navigation and rename operations when the environment provides them. Literal search is still necessary for string references and serialized names, but do not use global text replacement as a substitute for semantic analysis.

## Protected Contract Surfaces

Preserve these names unless the user explicitly requests and scopes a migration:

- external API fields and operation names;
- database tables, columns, stored procedures, and migration identifiers;
- serialized payload keys and persisted document fields;
- environment variables and configuration keys;
- URL parameters, query parameters, routes, and form field names;
- public package exports and documented consumer APIs;
- framework-required lifecycle methods, hooks, conventions, and magic names;
- third-party integration fields;
- event names, queue topics, telemetry dimensions, and metric names;
- dependency-injection tokens and runtime registration keys;
- reflection, decorators, annotations, and string-based property access;
- CSS selectors, template bindings, snapshots, and fixtures when they form runtime or test contracts;
- generated files whose source or generator should be changed instead.

An unusual external name is not automatically a defect.

## Translate at Boundaries

Keep a fixed external spelling while exposing a semantic internal name:

```ts
const customerId = apiResponse.cust_id;
```

For larger payloads, use an explicit adapter rather than spreading external terminology through the domain layer:

```ts
function mapApiOrder(apiOrder: ApiOrder): Order {
  return {
    orderId: apiOrder.ord_id,
    priceInCents: apiOrder.price,
  };
}
```

Do not silently change the serialized output while improving internal names.

## Apply Renames in a Controlled Order

1. Confirm the final rename map and protected spellings.
2. Rename definitions and traceable symbol references.
3. Update paired identifiers and semantic families only where necessary.
4. Update imports, exports, type relationships, overrides, and call sites.
5. Inspect literal references separately; change only those proven to refer to the internal symbol rather than a protected contract.
6. Update tests and documentation when they describe the internal identifier or behavior, not merely to hide a broken contract.
7. Format only the touched code needed for the rename.

Avoid combining the rename with extraction, reordering, control-flow changes, or formatting churn. A focused diff makes behavior preservation reviewable.

## Dynamic and Weakly Typed Code

Increase caution when references may not be statically discoverable:

```ts
handlerRegistry[handlerName]
object[propertyName]
container.resolve(serviceToken)
```

Search for relevant strings, registry construction, reflection, templates, configuration, and tests. If the dynamic surface cannot be traced confidently, keep the name or report the blocker rather than assuming the rename is safe.

## Cross-Module and Public Symbols

Before changing an exported symbol:

- identify every in-repository consumer;
- determine whether external consumers may exist;
- check whether compatibility aliases or a deprecation path are required;
- keep a contract change out of a behavior-preserving refactor unless explicitly authorized.

Do not treat repository-local search as proof that a public API has no external users.

## Verify Behavior

Run the repository's existing relevant checks in proportion to the change:

1. Targeted tests for the affected module or behavior.
2. Type checking or compilation.
3. Linting and static analysis.
4. Broader tests or builds when the symbol crosses modules or packages.
5. A final diff review for accidental value, control-flow, serialization, or formatting changes.

When a check is unavailable or already failing, report that limitation accurately. Do not claim behavior preservation solely because a textual rename completed.

Useful invariants include:

- runtime values and branches are unchanged;
- inputs and outputs retain the same shapes and keys;
- exported behavior and side effects are unchanged;
- only identifier references and necessary explanatory text changed;
- protected external spellings remain intact.

## Stop Conditions

Stop the rename and report what is unresolved when:

- the domain meaning supports multiple incompatible names;
- a dynamic reference cannot be traced safely;
- the change would alter a public or persisted contract outside the authorized scope;
- generated code would be overwritten by its generator;
- the required rename expands far beyond the requested files or modules;
- verification reveals a behavioral difference that cannot be explained as pre-existing.

Do not keep expanding the refactor to work around one of these conditions.

## Completion Report

Report:

- the meaningful rename groups applied;
- protected external names intentionally preserved;
- verification commands and their results;
- any unverified dynamic or external surfaces;
- any suggested follow-up that requires separate authorization.

Keep the report proportional to the change.
