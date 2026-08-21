---
name: intent-driven-naming
description: Design, audit, or safely refactor software identifiers when names materially affect comprehension, correctness, or contracts. Covers callables, parameters, locals, types, fields, schemas, messages, queries, and infrastructure across languages. Do not use for product, brand, file, branch, prose, or runtime-only work, or when identifiers must remain unchanged.
license: Apache-2.0
metadata:
  author: pabloamicodev
  version: "2.0.0"
---

# Intent-Driven Naming

Make important identifiers express durable semantic intent. Prefer the shortest idiomatic name that prevents a plausible, material wrong reading. A clear existing name is a successful `keep` decision.

## Route Only What the Task Needs

Read [references/naming-model.md](references/naming-model.md) for every task.

- New code: read [references/new-code-workflow.md](references/new-code-workflow.md).
- Audit only: read [references/audit-and-refactor.md](references/audit-and-refactor.md); do not edit.
- Authorized rename: read [references/audit-and-refactor.md](references/audit-and-refactor.md), [references/refactor-safety.md](references/refactor-safety.md), and [references/structural-analysis.md](references/structural-analysis.md).
- Callables or public parameters: read [references/callable-naming.md](references/callable-naming.md).
- Locals, captures, callbacks, accumulators, or intermediate values: read [references/local-variable-naming.md](references/local-variable-naming.md).
- Security, concurrency, distributed state, time, data/ML, observability, or resource ownership: read [references/high-risk-semantics.md](references/high-risk-semantics.md).
- Uncertain project conventions or an unlisted language: read [references/language-conventions.md](references/language-conventions.md).
- Multiple languages, schemas, generated clients, persisted state, or runtime names: read [references/polyglot-boundaries.md](references/polyglot-boundaries.md).

Load an ecosystem profile only when its exceptions affect an actively changed declaration: [TypeScript/JavaScript](references/typescript-javascript.md), [web frameworks](references/web-frameworks.md), [dynamic languages](references/dynamic-languages.md), [systems languages](references/systems-languages.md), [managed/mobile](references/managed-mobile-languages.md), [functional/concurrent](references/functional-concurrent-languages.md), or [data/infrastructure](references/data-infrastructure.md). Never load more than two profiles; use repository evidence for additional ecosystems.

## Work From Evidence

Determine meaning from declarations, types, assignments, data flow, callers, consumers, effects, failures, tests, domain vocabulary, and contracts. Generic spelling alone is not a defect. Use symbol-aware navigation when available and literal search only for strings and boundary spellings.

For each material identifier choose exactly one action: `keep`, `rename`, `map`, `migrate`, or `defer`. Prefer `map` when an internal alias can improve while a boundary remains fixed. Use `defer` when meaning or safety cannot be established.

## Preserve Scope and Behavior

- Do not turn naming work into architecture redesign, migration, dependency changes, or formatting churn.
- Treat public parameters, serialized keys, schemas, routes, environment keys, events, reflection strings, framework hooks, generated surfaces, ABI names, CLI flags, and infrastructure addresses as contracts.
- Do not assume a local is private when shorthand properties, named arguments, captures, macros, templates, or runtime lookup expose its spelling.
- For new code, apply names silently and return the requested implementation.
- For audits, rank only material findings by evidence, impact, confidence, and contract risk.
- For refactors, use the smallest coherent rename set and run the strongest relevant checks.

Report limitations honestly. Never claim behavior preservation from textual replacement alone.
