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

## Additional Ecosystem Cases

| ID | Prompt | Expected | Why |
|---|---|---|---|
| T21 | Implement a Rust parser that distinguishes raw, parsed, and validated configuration without unnecessary type suffixes. | Trigger | New systems code with representation and language-convention decisions. |
| T22 | Review this Java service for misleading domain names and preserve all interface overrides. | Trigger | Naming audit with object-oriented contract boundaries. |
| T23 | Refactor these C# async methods so their intent is clear without breaking the published .NET API. | Trigger | Behavior-preserving naming work with ecosystem-specific async conventions. |
| T24 | Design a Swift repository API whose argument labels read naturally at the call site. | Trigger | New public identifiers where labels are part of API meaning. |
| T25 | Improve the names in this Elixir pipeline and message protocol without changing registered atoms. | Trigger | Functional/concurrent naming with runtime protocol constraints. |
| T26 | Design SQL tables and columns for order totals, currencies, and timestamps with explicit units. | Trigger | New schema identifiers with correctness-critical semantics. |
| T27 | Rename these Terraform resources safely and account for existing state addresses. | Trigger | Infrastructure naming can change persisted operational identity. |
| T28 | Review this PowerShell module's cmdlet and parameter names for clarity and compatibility. | Trigger | Software identifier audit with public CLI conventions. |
| T29 | Rename internal C++ symbols while preserving exported C ABI names and generated bindings. | Trigger | Systems refactor with ABI and generation boundaries. |
| T30 | Create a Python API model that maps an external `customerId` field to idiomatic internal names. | Trigger | Polyglot boundary mapping and dynamic-language conventions. |

## Function and Local-Variable Cases

| ID | Prompt | Expected | Why |
|---|---|---|---|
| T31 | Rename this function so its declaration describes what it returns, then improve the variables inside it. | Trigger | Explicit callable-contract and intrafunction naming refactor. |
| T32 | Audit a method named `process` whose body uses `data`, `temp`, and `result`; determine which names are actually unclear. | Trigger | Evidence-based review of a callable and its local data flow. |
| T33 | Review whether `i`, `item`, and `acc` should stay short inside these small Go loops and reducers. | Trigger | Scope-sensitive local-variable naming with idiomatic exceptions. |
| T34 | Improve a public Python function's parameter and local names without breaking callers that use keyword arguments. | Trigger | Parameter naming crosses a source-level contract while locals may remain internal. |
| T35 | Name the function, closure parameters, intermediate values, and accumulator in this Rust transformation pipeline. | Trigger | Function-body generation across ownership-aware nested scopes. |
| T36 | Rename a JavaScript local variable but keep the emitted JSON property `customerId` unchanged. | Trigger | A local binding participates in property shorthand and serialization. |

## Borderline Review

When a result differs from `Expected`, inspect the description before adding more rules:

- A false negative may mean the key coding or audit trigger appears too late.
- A false positive may mean the description lacks a clear exclusion.
- Do not solve one case with an exhaustive list that broadens or narrows unrelated behavior.
- Repeat the suite after every description change.

## Passing Criteria

- All explicit naming audits and identifier refactors trigger.
- Representative non-trivial code-generation prompts trigger.
- Representative dynamic, systems, managed, functional, data, shell, and infrastructure prompts trigger.
- Explicit function-declaration, parameter, callback, accumulator, and local-variable naming requests trigger.
- Product, brand, file, branch, and prose naming prompts do not trigger.
- A safe-contract case triggers even when the correct outcome may be to preserve the external name.
