# Language and Project Convention Protocol

Use this protocol to translate semantic intent into names that are idiomatic for any language, framework, schema, or software artifact. The semantic model decides what a name means; this protocol decides how that meaning should appear locally.

## Do Not Treat Profiles as an Allowlist

The optional language profiles cover common ecosystems and recurring exceptions. They do not define the complete set of supported languages.

For an unlisted or domain-specific language:

1. Apply the language-independent semantic model.
2. Discover local conventions from authoritative repository evidence.
3. Preserve syntax-required and framework-required identifiers.
4. Render the semantic payload using the language's established casing, visibility, predicate, module, and API idioms.
5. Prefer a conservative no-op when the convention cannot be determined safely.

Do not borrow a profile merely because another language has similar syntax.

## Evidence Order

Determine local naming form from this evidence, in order:

1. User instructions and repository-level agent instructions.
2. Project style guides, contributing documentation, and architecture decisions.
3. Formatter, linter, compiler, analyzer, and code-generation configuration.
4. Stable patterns in the same package, module, layer, or schema.
5. Framework, standard-library, and language conventions.
6. The closest ecosystem profile in this skill only when it genuinely applies.

A large codebase can have intentional conventions per layer. Do not normalize them globally without evidence.

## Discover the Surface Convention

Before generating or renaming, identify:

- casing for locals, callables, types, constants, modules, packages, and schema fields;
- how exported, public, private, or internal visibility is expressed;
- predicate and boolean conventions;
- acronym and initialism treatment;
- conventional short locals, receivers, iterators, accumulators, and error bindings;
- generic type-parameter conventions;
- naming for async operations, effects, mutations, conversions, and fallible results;
- framework magic, protocol requirements, overrides, annotations, and generated members;
- whether parameter labels, field names, or aliases form part of a public API;
- naming constraints imposed by serialization, FFI, database, CLI, URL, or infrastructure boundaries.

Do not infer all of these from a single example file.

## Adapt in Two Passes

### Pass 1: Semantic Payload

Describe the concept without choosing syntax:

```text
collection of pending orders
price expressed in cents
operation that validates a shipping address
predicate asking whether checkout can be submitted
```

### Pass 2: Idiomatic Rendering

Render that payload for the concrete role and ecosystem:

```text
JavaScript local      pendingOrders
Python local          pending_orders
C# public property    PendingOrders
SQL relation alias    pending_orders
Elixir predicate      checkout_submittable?
```

The exact spelling may differ while the domain term remains continuous.

## Polyglot Continuity

Do not force identical casing or affixes across services and layers. Preserve the concept through explicit mappings:

```text
JSON field       customer_id
TypeScript       customerId
Python           customer_id
C# property      CustomerId
environment key  CUSTOMER_ID
```

Treat the serialized or interoperable spelling as a contract. Change internal aliases without silently changing the boundary.

When two layers intentionally use different business terms, document or preserve the translation instead of pretending they are identical.

## Language Semantics Can Affect Naming

Account for semantics that a universal camelCase checklist would miss:

- mutability versus immutable transformation;
- ownership, borrowing, lifetimes, or resource responsibility;
- nullable, optional, fallible, or result-bearing values;
- synchronous versus asynchronous APIs where the ecosystem encodes the distinction in names;
- effects, purity, commands, queries, events, messages, actors, and processes;
- exported versus package-private visibility;
- schema and infrastructure identifiers whose spelling affects persisted state;
- macros, metaprogramming, reflection, and runtime lookup.

Add semantic qualifiers only when they clarify a real distinction. Do not encode every type-system feature into every name.

## Preserve Required and Conventional Names

Do not rename these merely to satisfy the semantic model:

- language keywords and conventional receiver names;
- required entry points and lifecycle methods;
- interface, protocol, trait, superclass, or override members;
- operator and conversion conventions;
- framework-injected variables and template bindings;
- generated names and code-generation hooks;
- FFI, ABI, serialization, reflection, and runtime registration names;
- query aliases, schema fields, resource addresses, and CLI flags that form contracts.

Improve an internal alias or adapter when the required external spelling is unclear.

## Framework Conventions Override Generic Preferences

Names such as `req`, `res`, `ctx`, `self`, `cls`, `err`, `it`, or `_` can be idiomatic and sufficiently clear in the scopes where their ecosystem expects them. Do not expand them mechanically.

Likewise, a framework may require names that would look vague in ordinary business logic. Treat them as protocol vocabulary rather than style defects.

## Mixed-Language Changes

When one task crosses languages:

1. Keep a single domain vocabulary map.
2. Select the appropriate profile per changed artifact.
3. Preserve boundary spellings.
4. Review each language with its own tooling and conventions.
5. Do not apply a repository-wide text replacement across different syntaxes or generated outputs.

Load multiple profiles only when the task actually changes multiple ecosystems.

## Unknown-Language Fallback

If no profile applies, the skill still works. Use the semantic model, repository evidence, compiler or linter feedback, and conservative refactor safety.

Before completing, verify:

- the name tells the semantic truth;
- its form matches neighboring authoritative code;
- conventional short identifiers remain proportionate to scope;
- public and runtime contracts are preserved;
- no naming pattern from another language was imported without evidence.
