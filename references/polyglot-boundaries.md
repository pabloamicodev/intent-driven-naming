# Polyglot and Contract Boundaries

Preserve semantic continuity across languages without forcing identical spelling.

For each affected concept record its authoritative boundary spelling, internal aliases, owner, consumers, generated surfaces, persistence, and compatibility rule. Classify each spelling as:

- `contract`: preserve or migrate explicitly;
- `generated`: change the source and regenerate;
- `mapped`: keep an explicit serializer, annotation, adapter, or alias;
- `internal`: rename with native symbol-aware tooling.

Choose `keep`, `rename`, `map`, `migrate`, or `defer` for every affected spelling. Never hide a migration inside a cosmetic rename.

For a migration, update producer, compatibility mapping, consumers, tests, documentation, state moves, and rollback metadata as one authorized unit. For generated boundaries, change the schema or generator, regenerate with the pinned toolchain, review the diff, and verify every affected consumer.

Compile or analyze each changed language and verify serialization, runtime lookup, persisted state, and generated reproducibility separately. One passing ecosystem does not prove a cross-language change safe.
