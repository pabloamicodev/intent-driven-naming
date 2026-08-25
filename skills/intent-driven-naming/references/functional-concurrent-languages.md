# Functional and Concurrent Language Exceptions

For Haskell, OCaml, F#, Scala, Clojure, Erlang, Elixir, and similar ecosystems, preserve immutable transformation, algebraic data type, effect, pipeline, actor, process, and message semantics. Do not impose object-oriented setters, managers, or handlers.

Conventional `x`, `f`, `acc`, `_`, symbolic operators, and concise type parameters are valid in small mathematical or compositional scopes. Name intermediate stages only when they clarify branching, reuse, debugging, representation, or domain state.

Variants and constructors express distinct states or messages without always repeating their enclosing type. Predicate syntax, effect/fallibility forms, mutation markers, and pipeline conventions are ecosystem-specific.

Protect serialized union cases, message tags, registered processes, actors, topics, mailbox atoms, macros, symbols, protocols, type-class members, computation expressions, runtime dispatch, and JVM/.NET/BEAM/native interop names.
