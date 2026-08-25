---
name: intent-driven-naming
description: Design, audit, or safely refactor software identifiers when names materially affect comprehension, correctness, or contracts. Covers callables, parameters, locals, types, fields, schemas, messages, queries, and infrastructure across languages. Do not use for product, brand, file, branch, prose, or runtime-only work, or when identifiers must remain unchanged.
license: Apache-2.0
metadata:
  author: pabloamicodev
  version: "2.0.0"
---

# Intent-Driven Naming

Make important identifiers express durable intent. Prefer the shortest idiomatic name that prevents a plausible, material wrong reading. A clear name is a successful `keep` decision.

## Route Only What the Task Needs

Read [references/naming-model.md](references/naming-model.md) for every task.

- Workflow: new code → [new-code-workflow](references/new-code-workflow.md); audit → [audit-and-refactor](references/audit-and-refactor.md) without editing; authorized rename → [audit-and-refactor](references/audit-and-refactor.md), [refactor-safety](references/refactor-safety.md), and [structural-analysis](references/structural-analysis.md).
- Declaration: callable/public parameter → [callable-naming](references/callable-naming.md); local/capture/callback/accumulator → [local-variable-naming](references/local-variable-naming.md); type/field/collection/enum/constant/error/event/message → [declaration-naming](references/declaration-naming.md).
- Risk: security, concurrency, distributed state, time, data/ML, observability, or resources → [high-risk-semantics](references/high-risk-semantics.md); uncertain conventions or unlisted language → [language-conventions](references/language-conventions.md); polyglot, schema, generated, persisted, or runtime boundary → [polyglot-boundaries](references/polyglot-boundaries.md).

Load a profile only when its exceptions affect an active declaration: [TypeScript/JavaScript](references/typescript-javascript.md), [web frameworks](references/web-frameworks.md), [dynamic](references/dynamic-languages.md), [systems](references/systems-languages.md), [managed/mobile](references/managed-mobile-languages.md), [functional/concurrent](references/functional-concurrent-languages.md), or [data/infrastructure](references/data-infrastructure.md). Load at most two; use repository evidence for the rest.

## Decide From Evidence

Infer meaning from declarations, types, data flow, callers, consumers, effects, failures, tests, vocabulary, and contracts. Expand evidence only until a decision is supported; a change then requires complete coverage of its affected surface. Generic spelling alone is not a defect.

Choose `keep`, `rename`, `map`, `migrate`, or `defer`. Map when a boundary remains fixed. Defer when meaning or safety is unresolved.

## Preserve Scope and Behavior

- Do not expand naming work into architecture, dependencies, control flow, migration, or formatting churn.
- Treat public/named parameters, serialized keys, schemas, routes, environment keys, events, reflection, framework hooks, generated surfaces, ABI, CLI, and infrastructure identities as contracts.
- A local may expose its spelling through shorthand properties, captures, macros, templates, or runtime lookup.
- New code: apply names silently. Audit: report only material findings; omit full records unless requested or needed for a plan. Refactor: use the smallest coherent set and strongest relevant checks.

Report limitations honestly. Textual replacement alone never proves behavior preservation.
