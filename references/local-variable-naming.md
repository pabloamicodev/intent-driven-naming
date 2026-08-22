# Local Variable Naming

Local detail grows with reader distance, competing values, transformation depth, nested/asynchronous scope, and correctness risk.

- Translate fixed boundary spellings into internal vocabulary at the boundary.
- Name intermediates by the guarantee true on every path reaching that binding.
- Align plural collections with singular elements and name indexes or sets by membership semantics.
- Name accumulators by their invariant when scope, units, or competing aggregates make `acc`, `sum`, or `count` unclear.
- Distinguish boolean state, history, capability, policy, and requirement.
- Qualify errors and results by operation only when several coexist.
- Keep `i`, `x`, `err`, `ctx`, `item`, or `result` when a tiny conventional scope makes them unambiguous.

Do not bind every fluent or functional stage. A name earns its cost when it exposes a transition, enables reuse, improves diagnostics, or prevents a material wrong reading. Let the type, function, and tiny scope carry information before lengthening the local.

Before renaming inspect shadowing, destructuring, patterns, closures, captures, macros, templates, reflection, named arguments, logs, snapshots, and generated members. Object or record shorthand can turn a local spelling into an output contract; preserve the key explicitly when the binding changes.

Trace material bindings through assignments, branches, transformations, captures, and sinks. Keep the smallest coherent family and verify emitted shapes separately from references.
