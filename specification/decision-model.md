# Intent-Driven Naming Decision Specification

Version 1.0.0

This document defines the observable decisions required from a conforming implementation. `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` indicate requirement strength. The instructional references explain how to satisfy these requirements; this specification defines what success means.

## Decision Outcomes

Every reviewed identifier MUST resolve to one of these outcomes:

| Outcome | Meaning |
|---|---|
| `keep` | The existing name is clear, idiomatic, contract-bound, or not worth the churn. |
| `rename` | A supported internal rename produces material semantic gain. |
| `map` | An external spelling remains fixed while an internal semantic alias is introduced. |
| `migrate` | The desired name changes a public, persisted, stateful, or runtime contract and requires an explicit migration. |
| `defer` | Meaning or rename safety cannot be established from available evidence. |

A conforming implementation MUST allow `keep` and `defer`; it MUST NOT manufacture a rename to appear useful.

## Evidence Requirements

A naming decision MUST be supported by the identifier's actual role. Relevant evidence includes declarations, types, assignments, transformations, callers, consumers, return paths, side effects, tests, schemas, runtime registrations, and established domain vocabulary.

Generic spelling alone is insufficient evidence. An implementation MUST NOT reject `data`, `result`, `item`, `i`, `x`, `err`, or similar identifiers without considering scope and meaning.

When evidence conflicts, the implementation SHOULD prefer the smallest safe improvement. It MUST choose `defer` when a wrong interpretation could alter behavior or a protected contract.

## Semantic Requirements

A proposed name MUST:

- describe the actual concept, action, question, result, or effect;
- distinguish entities from identifiers and singular values from collections when needed;
- expose state, representation, relationship, cardinality, or unit when omission creates a plausible wrong interpretation;
- use the repository's canonical domain vocabulary;
- remain proportionate to its scope and role;
- follow the target language and framework conventions;
- avoid redundant type, container, or enclosing-scope words.

Related identifiers SHOULD form a coherent semantic family. Cross-language forms MAY differ in casing, affixes, visibility, and predicate syntax while preserving the same concept.

## Callable and Local Requirements

A callable name MUST agree with its observable behavior. Query-like names MUST NOT hide creation, persistence, publication, deletion, or other material effects.

Parameters MUST describe what callers provide. Public parameter names and argument labels MUST be treated as contracts when callers can bind by name.

Local variables SHOULD reveal meaningful data-flow states without narrating syntax. Short conventional bindings MAY remain when their scope removes ambiguity. Accumulators SHOULD state their invariant when multiple meanings, dangerous units, or long scopes coexist.

## Contract-Safety Requirements

A behavior-preserving refactor MUST preserve:

- runtime behavior, control flow, values, and side effects;
- public exports and documented APIs unless migration is authorized;
- serialized fields, schemas, database identifiers, environment keys, routes, and CLI surfaces;
- ABI, FFI, reflection, dependency-injection, registry, and string-based lookup names;
- protocol, trait, interface, override, framework, and generated-code requirements;
- property shorthand output keys, destructuring semantics, named arguments, captures, and stateful infrastructure addresses.

If a protected spelling is semantically weak, the implementation SHOULD use `map` rather than silently changing the boundary.

## Authorization Requirements

Audit-only work MUST remain read-only. A naming refactor MUST NOT expand into extraction, signature redesign, architecture changes, migrations, dependency changes, or broad formatting unless separately authorized.

The implementation MUST stop or choose `defer` when safe completion depends on unavailable dynamic references, unresolved domain meaning, generated sources outside scope, or a contract migration that was not authorized.

## Verification Requirements

An applied rename MUST use the strongest relevant checks available, in this order of concern:

1. Contract and serialized-shape checks.
2. Targeted behavioral tests.
3. Type checking, compilation, linting, or static analysis.
4. Cross-module, schema, query, or infrastructure verification.
5. Final diff review for value, control-flow, and formatting changes.

Unavailable or failing checks MUST be reported accurately. Textual replacement alone is not evidence of behavior preservation.

## Non-Compensable Failures

These failures automatically fail conformance regardless of stylistic quality:

- behavior regression;
- silent public or persisted contract change;
- invented domain meaning presented as fact;
- unauthorized mutation in audit mode;
- unreported dynamic or generated-code uncertainty;
- a migration represented as a behavior-preserving rename.
