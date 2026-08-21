---
name: intent-driven-naming
description: Improve identifier names in generated or existing application code. Use for code generation, naming audits, code review, and behavior-preserving refactors; not for product, brand, file, or prose naming.
---

# Intent-Driven Naming

Make important identifiers communicate durable semantic intent. Prefer the shortest name that remains unambiguous within its actual scope, and do not force a rename when the existing name is already clear.

## Route the Task

Read [references/naming-model.md](references/naming-model.md) for every task that uses this skill, then load only the workflow that applies:

- For new code, read [references/new-code-workflow.md](references/new-code-workflow.md).
- For an audit or review, read [references/audit-and-refactor.md](references/audit-and-refactor.md). Report findings without editing unless changes were explicitly requested.
- For an authorized rename or refactor, read both [references/audit-and-refactor.md](references/audit-and-refactor.md) and [references/refactor-safety.md](references/refactor-safety.md).
- For TypeScript, JavaScript, React, or React Query code, also read [references/typescript-react-patterns.md](references/typescript-react-patterns.md).

Do not read a mode-specific reference that does not apply.

## Shared Invariants

- Derive names from domain meaning, not primarily from programming-language type.
- Use the vocabulary already established by the user, codebase, contracts, and domain documentation.
- Add state, relationship, representation, scope, cardinality, or unit only when the distinction affects understanding or correctness.
- Treat generic words as context-dependent signals, not forbidden tokens.
- Keep naming pairs and semantic families synchronized.
- Preserve behavior, authorization boundaries, and protected external contracts.
- Prefer a local, high-confidence improvement over broad cosmetic churn.
- Follow established language and framework conventions when they conflict with a generic naming preference.

## Execute the Selected Mode

- **New code:** Apply the naming model while designing the code, then perform a silent semantic pass before completion. Do not add a naming report unless requested.
- **Audit only:** Rank findings by impact and confidence. Include protected names and justified no-op conclusions when relevant. Do not edit files.
- **Refactor:** Create the smallest safe rename set, protect boundaries, use symbol-aware changes when available, and verify behavior with the repository's existing checks.

## Completion Criteria

- Important identifiers remain understandable away from their declarations.
- Entities, IDs, collections, booleans, units, states, and transformations are distinguishable where the distinction matters.
- Related identifiers use consistent semantic families.
- Audit findings explain evidence, severity, confidence, and contract risk.
- Refactors preserve behavior and protected contracts, and verification results are reported accurately.
- Clear existing names remain unchanged.

## Boundaries

- Do not rename public APIs, schemas, serialized keys, environment variables, URL parameters, framework-required identifiers, or third-party fields merely for style.
- Do not edit generated code when its source or generator should be changed instead.
- Do not perform unrelated architectural refactors to support a naming change.
- Stop and report the ambiguity when a safe name depends on unresolved domain meaning or an untraceable dynamic contract.
