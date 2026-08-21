# Trigger Evaluation Cases

Use these cases to test whether the skill's `description` activates for the right requests. Run them without explicitly mentioning `$intent-driven-naming`, record whether the host selected the skill, and compare the result with `Expected`.

These cases evaluate routing only. They do not prescribe exact response wording.

## Positive Cases

| ID | Prompt | Expected | Difficulty | Locale | Why |
|---|---|---|---|---|---|
| T01 | Implement a TypeScript service that loads an organization's users and returns only active members. | Trigger | standard | en | New application code needs domain, collection, and state naming. |
| T02 | Refactor this module so ambiguous variables like `data`, `result`, and `item` communicate what they contain. Preserve behavior. | Trigger | standard | en | Explicit behavior-preserving identifier refactor. |
| T03 | Review this pull request for dangerous or misleading identifier names. Do not change files. | Trigger | standard | en | Explicit naming audit with a read-only boundary. |
| T04 | Build a React checkout form with state for the selected products, loading status, and submission errors. | Trigger | standard | en | New React code includes state families, booleans, callbacks, and errors. |
| T05 | Rename `price` safely throughout this package; it stores an integer number of cents. | Trigger | standard | en | Dangerous unit ambiguity and cross-module rename risk. |
| T06 | This API returns `usr_id`. Map it into our customer domain without changing the wire format. | Trigger | standard | en | Boundary translation and semantic internal naming. |
| T07 | Write a Python function that groups pending invoices by customer ID and totals their amounts. | Trigger | standard | en | New application code with collections, transformations, relationships, and IDs. |
| T08 | Check whether `client`, `customer`, and `account` are being used for the same concept in this repository. | Trigger | standard | en | Domain vocabulary and semantic continuity audit. |
| T09 | Rename the production database column `price` to `price_in_cents` without breaking consumers. | Trigger | standard | en | Naming change crosses a protected persisted contract and requires safety analysis. |
| T10 | The identifiers in this function already look reasonable. Audit them and tell me whether any rename is actually worth doing. | Trigger | standard | en | Tests the skill's ability to return a justified no-op. |
| T11 | Create a Go order-processing package with clear domain names and idiomatic short locals. | Trigger | standard | en | New application code plus language-convention exceptions. |
| T12 | Review these exported SDK types and suggest safer names without modifying the public API. | Trigger | standard | en | Naming review with an explicit public-contract boundary. |

## Negative Cases

| ID | Prompt | Expected | Difficulty | Locale | Why |
|---|---|---|---|---|---|
| T13 | Suggest ten names for a new AI accounting product. | Do not trigger | easy | en | Product and brand naming are out of scope. |
| T14 | Rename these image files using an SEO-friendly convention. | Do not trigger | easy | en | File naming is out of scope. |
| T15 | Rewrite this landing-page headline to sound more premium. | Do not trigger | easy | en | Prose and marketing copy are out of scope. |
| T16 | Explain lexical scope in JavaScript. | Do not trigger | easy | en | Conceptual programming explanation without identifier generation or review. |
| T17 | Find every file named `config.json` in this directory. | Do not trigger | easy | en | File discovery, not semantic identifier naming. |
| T18 | Fix the punctuation in this README. | Do not trigger | easy | en | Documentation copy edit. |
| T19 | Generate a UUID for this test fixture. | Do not trigger | easy | en | Value generation with no naming-sensitive application code. |
| T20 | Rename my Git branch to `feature/checkout`. | Do not trigger | easy | en | Repository branch naming, not code identifiers. |

## Additional Ecosystem Cases

| ID | Prompt | Expected | Difficulty | Locale | Why |
|---|---|---|---|---|---|
| T21 | Implement a Rust parser that distinguishes raw, parsed, and validated configuration without unnecessary type suffixes. | Trigger | standard | en | New systems code with representation and language-convention decisions. |
| T22 | Review this Java service for misleading domain names and preserve all interface overrides. | Trigger | standard | en | Naming audit with object-oriented contract boundaries. |
| T23 | Refactor these C# async methods so their intent is clear without breaking the published .NET API. | Trigger | standard | en | Behavior-preserving naming work with ecosystem-specific async conventions. |
| T24 | Design a Swift repository API whose argument labels read naturally at the call site. | Trigger | standard | en | New public identifiers where labels are part of API meaning. |
| T25 | Improve the names in this Elixir pipeline and message protocol without changing registered atoms. | Trigger | standard | en | Functional/concurrent naming with runtime protocol constraints. |
| T26 | Design SQL tables and columns for order totals, currencies, and timestamps with explicit units. | Trigger | standard | en | New schema identifiers with correctness-critical semantics. |
| T27 | Rename these Terraform resources safely and account for existing state addresses. | Trigger | standard | en | Infrastructure naming can change persisted operational identity. |
| T28 | Review this PowerShell module's cmdlet and parameter names for clarity and compatibility. | Trigger | standard | en | Software identifier audit with public CLI conventions. |
| T29 | Rename internal C++ symbols while preserving exported C ABI names and generated bindings. | Trigger | standard | en | Systems refactor with ABI and generation boundaries. |
| T30 | Create a Python API model that maps an external `customerId` field to idiomatic internal names. | Trigger | standard | en | Polyglot boundary mapping and dynamic-language conventions. |

## Function and Local-Variable Cases

| ID | Prompt | Expected | Difficulty | Locale | Why |
|---|---|---|---|---|---|
| T31 | Rename this function so its declaration describes what it returns, then improve the variables inside it. | Trigger | standard | en | Explicit callable-contract and intrafunction naming refactor. |
| T32 | Audit a method named `process` whose body uses `data`, `temp`, and `result`; determine which names are actually unclear. | Trigger | standard | en | Evidence-based review of a callable and its local data flow. |
| T33 | Review whether `i`, `item`, and `acc` should stay short inside these small Go loops and reducers. | Trigger | standard | en | Scope-sensitive local-variable naming with idiomatic exceptions. |
| T34 | Improve a public Python function's parameter and local names without breaking callers that use keyword arguments. | Trigger | standard | en | Parameter naming crosses a source-level contract while locals may remain internal. |
| T35 | Name the function, closure parameters, intermediate values, and accumulator in this Rust transformation pipeline. | Trigger | standard | en | Function-body generation across ownership-aware nested scopes. |
| T36 | Rename a JavaScript local variable but keep the emitted JSON property `customerId` unchanged. | Trigger | standard | en | A local binding participates in property shorthand and serialization. |

## Multilingual Positive Cases

| ID | Prompt | Expected | Difficulty | Locale | Why |
|---|---|---|---|---|---|
| T37 | Audita los nombres de esta función, incluidos sus parámetros y variables internas, sin cambiar el comportamiento. | Trigger | edge | es | Explicit Spanish naming audit with callable and local-variable scope. |
| T38 | Renomeie a variável local para esclarecer que contém o identificador selecionado, mas preserve a chave JSON pública. | Trigger | edge | pt | Portuguese identifier refactor with a protected serialization boundary. |

## Hard Negative and Boundary Cases

| ID | Prompt | Expected | Difficulty | Locale | Why |
|---|---|---|---|---|---|
| T39 | Fix the null-pointer bug in this function. Preserve every existing identifier exactly. | Do not trigger | adversarial | en | A code change explicitly excludes naming work. |
| T40 | Review this hot loop only for allocation and latency regressions; do not discuss naming or style. | Do not trigger | adversarial | en | A narrow performance review should not attract a naming specialist. |
| T41 | Audit this authentication handler only for exploitable security vulnerabilities. Keep identifiers unchanged. | Do not trigger | adversarial | en | A security audit with an explicit naming exclusion is outside scope. |
| T42 | Add the missing assertion to this existing test and preserve its API and identifiers verbatim. | Do not trigger | edge | en | A tightly scoped test edit does not require naming intervention. |
| T43 | Explain why this closure captures the outer variable. Do not modify the code. | Do not trigger | edge | en | Conceptual code explanation without a naming request. |
| T44 | Rewrite these inline comments so a new engineer can understand the algorithm. | Do not trigger | standard | en | Comment and prose editing are outside scope. |
| T45 | Suggest a memorable name for a new npm package. | Do not trigger | edge | en | Package branding is not semantic identifier design. |
| T46 | Choose a Docker image tag for today's staging build. | Do not trigger | edge | en | Artifact version labels are not application-code identifiers. |
| T47 | Rename these migration files so they sort chronologically. | Do not trigger | edge | en | File naming remains outside scope even in a database repository. |
| T48 | Replace the button label “Submit” with friendlier user-facing copy. | Do not trigger | edge | en | UI copy is prose, not a software identifier. |
| T49 | Write a concise Git commit message for this patch. | Do not trigger | standard | en | Commit-message writing is outside scope. |
| T50 | Rename these GitHub issue labels to make triage easier. | Do not trigger | standard | en | Repository workflow labels are not code identifiers. |
| T51 | Improve the headings and navigation labels in this developer guide. | Do not trigger | standard | en | Documentation information architecture is not identifier naming. |
| T52 | Generate a realistic customer name for this demo record. | Do not trigger | edge | en | Generating a value is different from naming a program symbol. |
| T53 | arregla el eror de null aca pero no canbies ningun nombre | Do not trigger | adversarial | es | Noisy Spanish bug-fix request explicitly preserves identifiers. |
| T54 | Dame diez nombres comerciales para una nueva función premium del producto. | Do not trigger | edge | es | Spanish product-feature branding is outside scope. |
| T55 | Reescreva esta documentação para ficar mais clara, sem alterar o código. | Do not trigger | edge | pt | Portuguese documentation editing should not activate the skill. |
| T56 | Schlage einen Produktnamen für unseren neuen KI-Assistenten vor. | Do not trigger | edge | de | German product naming is outside scope. |
| T57 | Renomme ma branche Git en `feature/paiement`. | Do not trigger | edge | fr | French Git branch naming remains outside scope. |
| T58 | plz format this fn only, dont rename vars or change logic | Do not trigger | adversarial | en | Noisy formatting request explicitly excludes identifier changes. |
| T59 | Check whether our dependency licenses are compatible with Apache-2.0. | Do not trigger | standard | en | License analysis is unrelated to software identifier naming. |
| T60 | Show me which Git branch is currently checked out. | Do not trigger | standard | en | Repository-state inspection is unrelated to identifier naming. |

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
