# Semantic Decision Kernel

An identifier is a compact claim about a program concept. It should encode only the distinctions needed to prevent a plausible, material wrong reading in its actual scope.

## Build a Semantic Record

For each important identifier determine the applicable fields; omit fields that add no distinction.

| Field | Question |
|---|---|
| Concept | What domain entity, value, action, policy, or event is this? |
| Role | How does it relate to another concept? |
| State | Which lifecycle state is guaranteed now? |
| Representation | Is it raw, parsed, normalized, validated, encoded, mapped, or persisted? |
| Cardinality | Is it one value, a collection, identifiers, an index, or an aggregate? |
| Unit or basis | Could currency, scale, grain, timezone, clock, or denominator be misread? |
| Ownership or trust | Does borrowed/owned, mutable/shared, trusted/untrusted, or secret/public matter? |
| Effect | For a callable, what observable result, I/O, mutation, publication, or failure occurs? |
| Scope | Which nearby concepts compete with this one, and how far does the name travel? |
| Contract | Is the spelling internal, cross-module, external, dynamic, generated, stateful, or unknown? |
| Materiality | Would a wrong read cost nothing, little, materially, or critically? |

Record evidence and confidence when auditing or refactoring. A formal plan may use `specification/rename-plan.schema.json`; ordinary generation does not need to emit the record.

## Evidence Order

1. User and domain terminology.
2. Public types, interfaces, schemas, and use cases.
3. Behavior: data flow, callers, consumers, effects, failures, and tests.
4. Stable vocabulary in the same module and adjacent layers.
5. UI, events, queries, and operational artifacts that reveal domain meaning.
6. A new term only when existing vocabulary is absent, contradictory, or misleading.

Frequency is evidence, not authority. Do not collapse `customer`, `account`, `user`, and `client` without proving that they denote the same concept.

## Decide Whether Change Is Material

Ask the counterfactual question:

> What plausible wrong assumption could a competent reader make from the current name, and what would it cost?

Rename only for a concrete `material` or `critical` wrong read that the candidate removes without greater noise or risk. `Critical` crosses a security, integrity, safety, or external-contract boundary. Typical distinctions include entity versus identifier, singular versus collection, current versus historical state, raw versus trusted representation, unit or time basis, source versus destination, and query versus side effect.

Keep the name when the alternative is merely longer, restates a type or enclosing scope, replaces an idiom, or lacks stronger evidence. Short names such as `i`, `x`, `err`, `ctx`, `self`, or `acc` can be correct in conventional, compact scopes.

## Choose an Action

- `keep`: clear, idiomatic, contract-bound, or not worth the churn.
- `rename`: traceable internal spelling with material semantic gain.
- `map`: preserve a boundary spelling and introduce an explicit internal alias.
- `migrate`: change a public, persisted, stateful, or runtime contract through an authorized compatibility plan.
- `defer`: meaning, ownership, consumers, or safety cannot be established.

## Compare Candidates Without Mechanical Scores

A candidate should be truthful, disambiguating, vocabulary-consistent, scope-proportionate, searchable, idiomatic, and contract-safe. Prefer a candidate only when it is clearly better across the material dimensions; preserve the current name when tradeoffs are marginal.

The semantic payload is portable while its spelling is not: `customerId`, `customer_id`, `CustomerID`, and `CUSTOMER_ID` may represent one concept in different ecosystems. Preserve explicit mappings across boundaries.
