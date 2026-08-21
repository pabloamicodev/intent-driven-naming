# Functional and Concurrent Language Patterns

Apply these patterns to Haskell, OCaml, F#, Scala, Clojure, Erlang, Elixir, and similar functional or actor-oriented code. Inspect the repository and language convention before choosing casing, symbolic names, predicate forms, module names, or effect terminology.

## Preserve the Programming Model

Do not force object-oriented naming patterns onto code organized around:

- immutable transformations;
- algebraic data types and pattern matching;
- pure functions and explicit effects;
- pipelines and composition;
- actors, processes, mailboxes, commands, and events;
- modules, namespaces, protocols, type classes, or traits;
- higher-order functions and concise mathematical abstractions.

Name the domain transformation or effect rather than inventing setters, managers, handlers, or mutable-state terminology.

## Values and Transformations

When intermediate stages are important, name their semantic state:

```text
raw orders
validated orders
pending orders
orders grouped by customer identifier
```

In a short composition or higher-order function, conventional bindings such as `x`, `f`, `acc`, or `_` may be sufficient. Expand them when the scope or domain interaction makes identity unclear.

Avoid sequence-only labels such as `data2`, `newState`, or `processedResult` when the transformation has a domain meaning.

## Types, Variants, and Constructors

Algebraic data types, union cases, enum variants, and constructors should represent distinct domain states or messages precisely:

```text
PendingPayment
AuthorizedPayment
DeclinedPayment
PaymentTimedOut
```

Do not duplicate the enclosing type in every variant when the language and scope already communicate it, unless public conventions or collision avoidance require the context.

Type parameters can remain concise in small generic abstractions. Use domain-oriented parameters when several types coexist or a public abstraction would otherwise be difficult to understand.

## Effects and Fallibility

Respect ecosystem conventions for optional, result-bearing, effectful, asynchronous, and stateful computations.

- Do not append `result`, `option`, `either`, `task`, `io`, or `effect` merely to restate the type.
- Add representation or lifecycle context when both raw and validated, synchronous and asynchronous, or pure and effectful forms coexist and names would otherwise collide.
- Preserve established suffixes or operators that communicate fallibility, mutation, or effect in the target language.

Names should not falsely imply purity, idempotence, or absence of side effects.

## Predicates

Use the language's predicate idiom:

- Clojure and languages with question-mark identifiers may use a trailing `?`.
- Elixir predicates commonly use `?` while guards and macros follow their own conventions.
- ML-family, Haskell, Scala, and F# projects may use `is`, `has`, or domain-specific predicate naming according to local style.

Do not add an `is` prefix blindly when the ecosystem has a clearer conventional form.

## Pipelines

Pipeline stages should preserve transformation meaning without naming every temporary value. Introduce a name when it improves debugging, branching, reuse, or semantic distinction.

Example intent:

```text
orders
-> keep pending orders
-> group by customer identifier
-> calculate totals in cents
```

If the pipeline remains linear and obvious, named intermediates may add noise. If multiple representations coexist, semantic stage names become valuable.

## Actors, Processes, and Messages

In Erlang, Elixir, Akka, Orleans-like systems, or other concurrent architectures, names can form runtime protocols.

Protect:

- registered process and actor names;
- message tags and tuple shapes;
- mailbox protocol atoms;
- topic, queue, and event names;
- supervisor and child identifiers;
- distributed node or registry names;
- serialization fields and versioned events.

Internal function and binding names can improve while protocol values remain stable.

## Macros, Symbols, and Dynamic Dispatch

Clojure vars, Lisp symbols, Elixir macros, Scala implicits or givens, F# computation expressions, type-class members, and protocol implementations may be discovered or expanded indirectly. Trace macro use, reflection, generated code, and runtime registration before renaming.

Symbolic operators can be idiomatic in mathematical or combinator libraries. Preserve them when their meaning is established and local; do not replace them solely to satisfy a word-based naming preference.

## Cross-Language Interop

Functional languages often interoperate with JVM, .NET, JavaScript, native, or BEAM ecosystems. Preserve foreign interface names and translate them through local aliases or wrapper modules.

Do not rename an override, protocol member, exported function, union case serialized externally, or message tag without compatibility analysis.

## Review Checklist

- Does the naming match functional, immutable, pipeline, or actor semantics rather than an imposed object model?
- Are conventional concise bindings proportionate to their scope?
- Do transformations and variants express meaningful domain states?
- Are predicates rendered with the target language's idiom?
- Do names accurately reflect effects, fallibility, and side effects?
- Are actor names, message tags, serialized variants, macros, and interop contracts protected?
