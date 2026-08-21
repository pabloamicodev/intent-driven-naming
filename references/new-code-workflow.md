# New-Code Workflow

Use naming as part of design, not as a report added after implementation.

1. Establish the domain vocabulary from the request, nearby code, contracts, and tests. Do not invent business distinctions.
2. Inventory identifiers where a wrong reading matters: entities and IDs, collections and elements, lifecycle states, representations, units, effects, errors, events, captures, and cross-layer concepts.
3. Apply the semantic record from `naming-model.md`, then render it using the repository's language and framework conventions.
4. Keep related names as one semantic family across the declaration, parameters, local stages, errors, effects, and return value.
5. Perform a silent final pass. Return the requested code, not a naming essay, unless rationale was requested.

Name a transformed value by what it represents now, not by sequence words such as `processed`, `updated`, or `final`. Use plural collections and aligned singular elements. Name maps, sets, and aggregates by membership or indexing semantics when needed. Add units, trust states, or time bases only when confusion is plausible.

Do not bind every pipeline stage. Introduce a local when it clarifies a domain transition, supports reuse or diagnostics, or prevents confusion. Keep conventional short bindings in tiny scopes.

Before completion verify:

- callable names agree with observable results, effects, and failure behavior;
- parameters describe caller inputs and public labels remain compatible;
- meaningful local stages remain distinguishable without narration;
- vocabulary stays continuous across related identifiers;
- no type word, container word, or enclosing context is repeated unnecessarily;
- no protected external spelling was changed for style.
