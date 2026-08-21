---
name: intent-driven-naming
description: Improve identifiers when naming quality is material to code generation, an explicit naming audit, or a behavior-preserving refactor. Covers functions, parameters, locals, types, schemas, queries, and infrastructure across languages. Do not use when the task explicitly preserves identifiers, concerns only runtime behavior, or names products, brands, files, branches, or prose.
---

# Intent-Driven Naming

Make important identifiers communicate durable semantic intent. Prefer the shortest name that remains unambiguous within its actual scope, and do not force a rename when the existing name is already clear.

## Route the Task

Read [references/naming-model.md](references/naming-model.md) for every task that uses this skill, then load only the workflow and specialized references that apply.

Read [references/language-conventions.md](references/language-conventions.md) when conventions are uncertain, the language is unlisted, or public and runtime contracts make surface form important. For a small local task with clear repository conventions, use the selected profile and nearby authoritative code without loading the extra protocol.

For a change crossing two or more languages, schemas, generated boundaries, or runtime naming systems, read [references/polyglot-boundaries.md](references/polyglot-boundaries.md). Use it as the shared mapping protocol. Load a full language profile only for an artifact whose declarations are actively generated or changed, and never load more than two full profiles at once; inspect additional ecosystems from local authoritative evidence instead.

Select the workflow:

- For new code, read [references/new-code-workflow.md](references/new-code-workflow.md).
- For an audit or review, read [references/audit-and-refactor.md](references/audit-and-refactor.md). Report findings without editing unless changes were explicitly requested.
- For an authorized rename or refactor, read both [references/audit-and-refactor.md](references/audit-and-refactor.md) and [references/refactor-safety.md](references/refactor-safety.md).

When function or method declarations, constructors, commands, queries, handlers, or public parameters are central, read [references/callable-naming.md](references/callable-naming.md).

When local bindings, callback parameters, closure captures, accumulators, indexes, errors, or intermediate results are central, read [references/local-variable-naming.md](references/local-variable-naming.md).

Select the relevant language profile for each actively changed part of the task, subject to the polyglot limit above:

- TypeScript, JavaScript, Node.js, or browser modules: read [references/typescript-javascript.md](references/typescript-javascript.md).
- React, React Query, Vue, Svelte, Angular, or comparable component frameworks: also read [references/web-frameworks.md](references/web-frameworks.md).
- Python, Ruby, or PHP: read [references/dynamic-languages.md](references/dynamic-languages.md).
- Go, Rust, C, or C++: read [references/systems-languages.md](references/systems-languages.md).
- Java, Kotlin, C#, Swift, or Dart: read [references/managed-mobile-languages.md](references/managed-mobile-languages.md).
- Haskell, OCaml, F#, Scala, Clojure, Erlang, or Elixir: read [references/functional-concurrent-languages.md](references/functional-concurrent-languages.md).
- SQL, data pipelines, shell scripts, PowerShell, schemas, or infrastructure as code: read [references/data-infrastructure.md](references/data-infrastructure.md).

The profiles are refinements, not a supported-language allowlist. For an unlisted language, apply the naming model and the repository-discovery protocol in `language-conventions.md`. Do not load an unrelated profile merely because its syntax looks similar. Do not read a mode or profile reference that does not apply.

## Shared Invariants

- Derive names from domain meaning, not primarily from programming-language type.
- Choose semantic meaning before translating it into the target language's casing, affixes, visibility, and API conventions.
- Use the vocabulary already established by the user, codebase, contracts, and domain documentation.
- Add state, relationship, representation, scope, cardinality, or unit only when the distinction affects understanding or correctness.
- Treat generic words as context-dependent signals, not forbidden tokens.
- Keep naming pairs and semantic families synchronized.
- Keep callable declarations, parameters, local data-flow stages, errors, and returned values semantically coherent.
- Preserve behavior, authorization boundaries, and protected external contracts.
- Prefer a local, high-confidence improvement over broad cosmetic churn.
- Follow established language and framework conventions when they conflict with a generic naming preference.
- Preserve framework magic, protocol requirements, overrides, schema fields, and interop names as contracts.

## Execute the Selected Mode

- **New code:** Apply the naming model while designing the code, then perform a silent semantic pass before completion. Do not add a naming report unless requested.
- **Audit only:** Rank findings by impact and confidence. Include protected names and justified no-op conclusions when relevant. Do not edit files.
- **Refactor:** Create the smallest safe rename set, protect boundaries, use symbol-aware changes when available, and verify behavior with the repository's existing checks.

## Completion Criteria

- Important identifiers remain understandable away from their declarations.
- Callable names state their observable action, result, question, or effect, while parameters and locals reveal meaningful data flow at a scope-appropriate level.
- Entities, IDs, collections, booleans, units, states, and transformations are distinguishable where the distinction matters.
- Related identifiers use consistent semantic families.
- Names are idiomatic for the target language and role without losing cross-layer domain continuity.
- Audit findings explain evidence, severity, confidence, and contract risk.
- Refactors preserve behavior and protected contracts, and verification results are reported accurately.
- Clear existing names remain unchanged.

## Boundaries

- Do not rename public APIs, schemas, serialized keys, environment variables, URL parameters, framework-required identifiers, overrides, protocol requirements, or third-party fields merely for style.
- Do not assume an intrafunction rename is private when property shorthand, destructuring, named arguments, closures, reflection, serialization, or generated code exposes the spelling.
- Do not edit generated code when its source or generator should be changed instead.
- Do not perform unrelated architectural refactors to support a naming change.
- Stop and report the ambiguity when a safe name depends on unresolved domain meaning or an untraceable dynamic contract.
