# Go, Rust, C, and C++ Patterns

Apply these patterns to systems code after inspecting package, module, ABI, platform, and repository conventions. These ecosystems often use concise locals and encode visibility or ownership through language structure; do not translate a verbose application-style convention mechanically.

## Go

Go names are strongly shaped by package context and exported visibility.

- Preserve concise receiver names that are consistent for the type.
- Short locals such as `i`, `n`, `ok`, `err`, `ctx`, `r`, and `w` can be idiomatic in narrow scopes.
- Exported names must communicate enough meaning without repeating the package name.
- Keep initialism treatment consistent with the repository and public API.
- Do not add `Get` automatically when the established package API uses a shorter accessor name.
- Small behavior-focused interfaces may use an idiomatic role name; do not force a suffix when the abstraction does not warrant one.

Example of proportionate local naming:

```go
orders, err := repository.ListPendingOrders(ctx, customerID)
if err != nil {
    return nil, err
}
```

`ctx` and `err` are clear conventions here. `orders` and `customerID` preserve the domain meaning.

Treat exported identifiers, struct tags, JSON names, database tags, command flags, plugin symbols, generated interfaces, and reflection-based registrations as contracts.

## Rust

Respect Rust casing and API semantics:

- functions, methods, variables, modules, and fields typically use `snake_case`;
- types, traits, enums, and variants typically use `UpperCamelCase`;
- constants and statics follow the repository's constant convention;
- short closure bindings are acceptable in small iterator chains when the entity remains clear;
- names should reflect ownership or representation only when competing forms make the distinction relevant.

Conversion prefixes can carry established semantics. Preserve or use `as_`, `to_`, and `into_` according to the API's conversion and ownership behavior rather than treating them as interchangeable wording.

Predicates commonly read clearly with forms such as:

```rust
is_authenticated
has_active_subscription
can_retry_payment
```

Do not append `result`, `option`, `ref`, or `owned` merely to restate a type. Use a semantic qualifier when multiple fallible, borrowed, owned, parsed, or validated representations coexist.

Trait methods, enum variants, serde names, FFI symbols, macros, feature flags, and unsafe boundaries may be public or generated contracts.

## C and C++

C and C++ repositories vary widely. Discover local conventions before changing casing, prefixes, suffixes, namespace structure, or member notation.

Potentially meaningful existing patterns include:

- subsystem or library prefixes used to avoid linkage collisions;
- exported ABI names and calling-convention macros;
- struct tags, typedefs, enum constants, and preprocessor macros;
- member or parameter affixes used consistently by the project;
- ownership, lifetime, buffer length, capacity, and unit distinctions;
- template parameter and concept naming conventions;
- overloaded operators and standard-library-compatible APIs.

Do not remove a prefix as “Hungarian notation” until its actual ABI, subsystem, generated-code, or ownership role is understood.

Names involving buffers and resource management should preserve correctness-critical distinctions:

```text
buffer length versus buffer capacity
owned handle versus borrowed handle
source bytes versus destination bytes
timeout in milliseconds versus seconds
```

Add those distinctions only when both forms coexist or a wrong assumption is plausible.

Macros, include guards, linker-visible symbols, callbacks registered through function pointers, reflection systems, serialization libraries, and generated bindings require contract analysis before rename.

## Systems-Specific Safety

A rename can appear behavior-preserving while breaking:

- ABI or FFI consumers;
- symbol lookup and dynamic loading;
- build-system variables and feature flags;
- generated bindings;
- linker scripts and platform entry points;
- serialization or reflection metadata;
- unsafe code assumptions documented through names.

Inspect build files and non-code references when the symbol crosses these boundaries.

## Review Checklist

- Are conventional short locals and receiver names proportionate to their scope?
- Does visibility follow package, module, or linkage conventions?
- Are acronym and initialism forms consistent locally?
- Are ownership, lifetime, capacity, unit, and representation distinctions explicit only where needed?
- Are trait, interface, macro, ABI, FFI, tag, and generated names protected?
- Does the proposed name repeat package, namespace, or type context unnecessarily?
