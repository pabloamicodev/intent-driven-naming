# New-Code Workflow

Apply naming during design; return the requested implementation without a naming report.

1. Establish domain vocabulary from the request, nearby code, contracts, and tests; do not invent business distinctions.
2. Inventory material entities/IDs, collections/elements, lifecycle states, representations, units, effects, errors, events, captures, and cross-layer concepts.
3. Apply `naming-model.md`, render using repository conventions, and keep declarations, parameters, local stages, errors, effects, and results as one semantic family.
4. Map fixed boundary spellings into internal vocabulary explicitly.
5. Apply the wrong-read and all-path guarantee tests, then remove words already supplied by types or scope.

Name a transformed value by its proven current meaning, not sequence words such as `processed` or `final`. Align collections and elements. Name maps, sets, and aggregates by membership or indexing when needed. Add units, trust, or time bases only when confusion is plausible.

Do not bind every pipeline stage. Introduce a local when it clarifies a domain transition, supports reuse or diagnostics, or prevents confusion. Keep conventional short bindings in tiny scopes.

Before completion verify callable contracts, public labels, meaningful local stages, vocabulary continuity, protected spellings, and removal of redundant type or container words.
