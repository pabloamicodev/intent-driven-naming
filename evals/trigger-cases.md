# Trigger Evaluation Cases

Use these cases to test whether the skill's `description` activates for the right requests. Run them without explicitly mentioning `$intent-driven-naming`, record whether the host selected the skill, and compare the result with `Expected`.

These cases evaluate routing only. They do not prescribe exact response wording.

## Positive Cases

| ID | Prompt | Expected | Why |
|---|---|---|---|
| T01 | Implement a TypeScript service that loads an organization's users and returns only active members. | Trigger | New application code needs domain, collection, and state naming. |
| T02 | Refactor this module so ambiguous variables like `data`, `result`, and `item` communicate what they contain. Preserve behavior. | Trigger | Explicit behavior-preserving identifier refactor. |
| T03 | Review this pull request for dangerous or misleading identifier names. Do not change files. | Trigger | Explicit naming audit with a read-only boundary. |
| T04 | Build a React checkout form with state for the selected products, loading status, and submission errors. | Trigger | New React code includes state families, booleans, callbacks, and errors. |
| T05 | Rename `price` safely throughout this package; it stores an integer number of cents. | Trigger | Dangerous unit ambiguity and cross-module rename risk. |
| T06 | This API returns `usr_id`. Map it into our customer domain without changing the wire format. | Trigger | Boundary translation and semantic internal naming. |
| T07 | Write a Python function that groups pending invoices by customer ID and totals their amounts. | Trigger | New application code with collections, transformations, relationships, and IDs. |
| T08 | Check whether `client`, `customer`, and `account` are being used for the same concept in this repository. | Trigger | Domain vocabulary and semantic continuity audit. |
| T09 | Rename the production database column `price` to `price_in_cents` without breaking consumers. | Trigger | Naming change crosses a protected persisted contract and requires safety analysis. |
| T10 | The identifiers in this function already look reasonable. Audit them and tell me whether any rename is actually worth doing. | Trigger | Tests the skill's ability to return a justified no-op. |
| T11 | Create a Go order-processing package with clear domain names and idiomatic short locals. | Trigger | New application code plus language-convention exceptions. |
| T12 | Review these exported SDK types and suggest safer names without modifying the public API. | Trigger | Naming review with an explicit public-contract boundary. |

## Negative Cases

| ID | Prompt | Expected | Why |
|---|---|---|---|
| T13 | Suggest ten names for a new AI accounting product. | Do not trigger | Product and brand naming are out of scope. |
| T14 | Rename these image files using an SEO-friendly convention. | Do not trigger | File naming is out of scope. |
| T15 | Rewrite this landing-page headline to sound more premium. | Do not trigger | Prose and marketing copy are out of scope. |
| T16 | Explain lexical scope in JavaScript. | Do not trigger | Conceptual programming explanation without identifier generation or review. |
| T17 | Find every file named `config.json` in this directory. | Do not trigger | File discovery, not semantic identifier naming. |
| T18 | Fix the punctuation in this README. | Do not trigger | Documentation copy edit. |
| T19 | Generate a UUID for this test fixture. | Do not trigger | Value generation with no naming-sensitive application code. |
| T20 | Rename my Git branch to `feature/checkout`. | Do not trigger | Repository branch naming, not code identifiers. |

## Borderline Review

When a result differs from `Expected`, inspect the description before adding more rules:

- A false negative may mean the key coding or audit trigger appears too late.
- A false positive may mean the description lacks a clear exclusion.
- Do not solve one case with an exhaustive list that broadens or narrows unrelated behavior.
- Repeat the suite after every description change.

## Passing Criteria

- All explicit naming audits and identifier refactors trigger.
- Representative non-trivial code-generation prompts trigger.
- Product, brand, file, branch, and prose naming prompts do not trigger.
- A safe-contract case triggers even when the correct outcome may be to preserve the external name.
