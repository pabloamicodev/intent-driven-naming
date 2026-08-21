# Intent-Driven Naming Decision Specification

Version 2.0.0

This document defines observable requirements for a conforming implementation. `MUST`, `MUST
NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` indicate requirement strength.

## Semantic record

Every identifier considered in audit or refactor mode MUST have one semantic record. The portable
shape is defined by `semantic-record.schema.json`. Its stable `symbol_id` and source location
identify the declaration; identifier spelling alone is never identity.

The record MUST contain:

- evidence from definitions, assignments, types, callers, consumers, tests, contracts, or runtime
  lookup surfaces;
- a meaning with a domain concept and every material role, state, representation, cardinality,
  unit or basis, ownership or trust stage, effect, and scope dimension;
- a plausible `wrong_read`, or `null` when the name is not materially misleading;
- `none`, `low`, `material`, or `critical` materiality for the wrong-read cost;
- exactly one decision, confidence level, contract risk, protected spellings, and unresolved
  surfaces.

The wrong-read test is counterfactual: could a competent maintainer plausibly choose an incorrect
operation, unit, state, trust assumption, representation, or boundary because of this name? Style
preference, length, and membership in a prohibited-word list do not satisfy the test.

## Decision outcomes

| Outcome | Normative meaning |
|---|---|
| `keep` | Clear, idiomatic, contract-bound, or not worth churn. |
| `rename` | Evidence supports an internal rename with material semantic gain. |
| `map` | A protected spelling remains fixed while an internal semantic alias is introduced. |
| `migrate` | A public, persisted, generated, dynamic, or stateful identity changes under explicit migration authorization. |
| `defer` | Meaning or rename safety cannot be established from available evidence. |

A conforming implementation MUST allow `keep` and `defer`. `rename`, `map`, and `migrate` require
a distinct proposed name, a non-empty wrong read, `material` or `critical` materiality, and at least
medium confidence. `map`
requires at least one protected spelling.
`migrate` requires explicit migration authorization. A direct `rename` MUST NOT be used for an
external, dynamic, generated, stateful, or unknown-risk symbol. Unknown contract risk MUST block
all changing decisions.

## Name fitness

A proposed name MUST describe the actual concept, action, question, result, or effect and MUST use
repository vocabulary when that vocabulary is consistent with behavior. It MUST expose a semantic
dimension only when omission creates a plausible wrong read.

Related declarations, parameters, locals, errors, results, and effects SHOULD form one coherent
family. Public parameters and argument labels are contracts when callers bind by name. Query-like
callable names MUST NOT hide persistence, publication, authorization, deletion, or other material
effects. Short conventional locals MAY remain when scope removes ambiguity.

High-risk domains require special scrutiny:

- security and privacy: trust, validation, authentication, authorization, sensitivity, and
  redaction stages;
- distributed and concurrent systems: ownership, mutability, consistency, snapshot status,
  freshness, retry, idempotency, and lock scope;
- time: instant versus duration, wall versus monotonic clock, timezone, deadline, and unit;
- data and ML: encoding, shape, axes, sampling, normalization, labels, predictions, and units;
- observability: metric identity, label keys and values, cardinality, and stable telemetry names;
- resources and performance: bytes versus elements, capacity versus length, ownership, lifetime,
  and allocation behavior.

A name MUST NOT claim a stronger trust, consistency, normalization, safety, or validation property
than the evidence proves.

## Contract and authorization safety

A behavior-preserving refactor MUST preserve runtime behavior, values, control flow, side effects,
public exports, serialized fields, schemas, database identities, environment keys, routes, flags,
ABI/FFI, reflection, dependency injection, registries, protocol and override requirements,
generated sources, property shorthand output, named arguments, captures, and infrastructure state.

Audit mode is read-only. Naming authorization does not authorize extraction, signature redesign,
architecture changes, dependency changes, broad formatting, or migration. Unresolved dynamic or
generated surfaces require `defer`; they MUST NOT be hidden by a confidence claim.

## Rename plans and verification

Changes spanning more than a trivial local edit SHOULD be expressed as a
`rename-plan.schema.json` document and checked with
`scripts/runtime/validate_rename_plan.py`. Structural analysis SHOULD use an AST, language server,
compiler index, or symbol graph where available; textual search is supplementary evidence for
strings, configuration, templates, and dynamic lookup. The plan MUST record analysis methods,
reference coverage, dynamic surfaces checked, and a maximum authorized changed-symbol count.
Every changing plan MUST include symbol-aware collision or shadowing evidence.

Applied changes MUST run the strongest relevant contract checks, targeted behavior tests,
type/compile/static checks, cross-module or state checks, and final diff review. A changing plan
requires at least one verification command and one collision check. Non-internal risk requires an explicit contract check.
Non-internal changes require complete reference coverage. Dynamic changes require at least one
checked runtime surface. Migrations require an executable rollback command. Unavailable or failing
checks MUST be reported accurately.

## Non-compensable failures

Behavior regression, silent contract change, invented meaning, unauthorized mutation, unreported
dynamic or generated uncertainty, fabricated verification, and a migration represented as a local
rename fail conformance regardless of aggregate style or benchmark score.
