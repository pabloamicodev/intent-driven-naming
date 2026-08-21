---
name: intent-driven-naming
description: Improve function, method, parameter, local-variable, type, schema, query, and infrastructure identifiers across languages. Use for code generation, naming audits, review, and behavior-preserving refactors; not for product, brand, file, branch, or prose naming.
---

# Intent-Driven Naming

Make important identifiers communicate durable semantic intent. Prefer the shortest name that remains unambiguous within its actual scope, and do not force a rename when the existing name is already clear.

## Route the Task

Read both [references/naming-model.md](references/naming-model.md) and [references/language-conventions.md](references/language-conventions.md) for every task that uses this skill, then load only the workflow and language profile that apply.

Select the workflow:

- For new code, read [references/new-code-workflow.md](references/new-code-workflow.md).
- For an audit or review, read [references/audit-and-refactor.md](references/audit-and-refactor.md). Report findings without editing unless changes were explicitly requested.
- For an authorized rename or refactor, read both [references/audit-and-refactor.md](references/audit-and-refactor.md) and [references/refactor-safety.md](references/refactor-safety.md).

When the affected code creates, reviews, or renames a callable or its body, also read [references/function-and-local-naming.md](references/function-and-local-naming.md). This includes functions, methods, constructors, parameters, local bindings, callbacks, closure captures, accumulators, and intermediate results.

Select at most the relevant language profile for each affected part of the task:

- TypeScript, JavaScript, Node.js, or browser UI frameworks: read [references/typescript-javascript.md](references/typescript-javascript.md).
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
