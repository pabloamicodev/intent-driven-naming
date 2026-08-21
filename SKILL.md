---
name: intent-driven-naming
description: Apply intent-driven naming when generating, reviewing, modifying, or refactoring application code. Use for code generation and identifier audits that need clearer domain meaning, state, scope, transformations, relationships, or units while preserving behavior; do not use for product, brand, file, or prose naming.
---

# Intent-Driven Naming

Make every important identifier communicate semantic intent rather than its programming-language type. Prefer the shortest name that remains unambiguous within its scope.

## Required Reference

Read [references/naming-guidelines.md](references/naming-guidelines.md) before performing a naming-sensitive implementation, review, or refactor. Use the guideline as decision criteria, not as a mechanical ban list.

## Choose the Scenario

### Generate New Code

1. Establish the domain vocabulary already used by the request and codebase.
2. Name important values by domain meaning, state, scope, transformation, relationship, or unit when those distinctions matter.
3. Keep related identifiers synchronized, including collections and elements, entities and IDs, booleans, state pairs, callbacks, and query families.
4. Before completing the implementation, perform a silent semantic naming pass using the final review in the reference.

Do not add a separate naming report unless the user asks for one.

### Audit or Refactor Existing Code

1. If the user requests an audit or review only, report findings without editing code.
2. If changes are requested, prioritize dangerous names, then misleading, ambiguous, and inconsistent names.
3. Preserve runtime behavior and keep the diff limited to the requested scope.
4. Preserve external contracts, public APIs, schemas, serialized keys, environment variables, URL parameters, framework conventions, and third-party integration fields unless the user explicitly authorizes changing them.
5. When an external name cannot change, translate it to a semantic internal name at the boundary when useful.
6. Avoid unrelated architectural refactors and broad cosmetic rename churn.

## Working Rules

- Follow the codebase's established domain vocabulary unless it is demonstrably misleading.
- Treat generic names as context-dependent, not automatically invalid.
- Add qualifiers only when they resolve real ambiguity.
- Describe the resulting state of a transformation instead of using sequence words such as `new`, `updated`, `processed`, or `final`.
- Keep names searchable without making them unnecessarily long.
- Do not substitute one business term for another unless they represent the same concept.

## Completion Criteria

- Important identifiers remain understandable away from their declarations.
- IDs, entities, collections, booleans, units, states, and transformations are distinguishable where correctness or clarity depends on them.
- Related identifiers use consistent semantic families.
- Existing behavior and protected external contracts remain unchanged unless the user requested otherwise.
