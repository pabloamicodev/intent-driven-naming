# Semantic Decision Kernel

An identifier is a compact claim about a program concept. Encode only distinctions needed to prevent a plausible, material wrong reading in its actual scope.

## Build a Semantic Record

For each important identifier determine only the applicable fields:

| Field | Question |
|---|---|
| Concept and role | What domain entity, value, action, policy, or relation is this? |
| State and representation | What lifecycle state or transformation is guaranteed now? |
| Cardinality | Is it one value, a collection, IDs, an index, or an aggregate? |
| Unit or basis | Could scale, grain, timezone, clock, or denominator be misread? |
| Ownership or trust | Does ownership, mutability, authority, trust, or sensitivity matter? |
| Effect | What result, I/O, mutation, publication, or failure occurs? |
| Scope | Which nearby concepts compete, and how far does the name travel? |
| Contract | Is spelling internal, external, dynamic, generated, stateful, or unknown? |
| Materiality | What would a plausible wrong read cost? |

A state or guarantee must hold on every path reaching the named value; intent or a happy path is not evidence. Formal plans may use `specification/rename-plan.schema.json`; ordinary work keeps the record internal.

## Evidence Order

1. User and domain terminology.
2. Public types, schemas, interfaces, and use cases.
3. Data flow, callers, consumers, effects, failures, and tests.
4. Stable vocabulary in the same module and adjacent layers.
5. Operational artifacts that reveal domain meaning.
6. A new term only when existing vocabulary is absent or false.

Frequency is evidence, not authority. Do not collapse `customer`, `account`, `user`, and `client` without proving equivalence.

## Decide and Select

Ask: *What plausible wrong assumption could a competent reader make, and what would it cost?* Change only for a `material` or `critical` wrong read; critical crosses security, integrity, safety, or external contracts. Keep names whose alternatives merely restate types or scope, replace idiom, or lack stronger evidence.

Choose `keep`, `rename`, `map`, `migrate`, or `defer`. Map fixed boundaries to clearer internal vocabulary. Migrate only with explicit authority. Defer when meaning or safety remains uncertain.

Use types, namespaces, signatures, and scope as free context. Reject candidates that are false on a reachable path, hide an effect, conflict with domain vocabulary, or change a contract. Among survivors prefer semantic truth, removal of the wrong read, vocabulary consistency, ecosystem idiom/searchability, then brevity. Keep the current name when no candidate clearly dominates it.

Semantic payload is portable while spelling is not: `customerId`, `customer_id`, and `CustomerID` can represent one concept. Preserve explicit mappings across boundaries.
