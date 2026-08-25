# Convention Discovery

The semantic model decides meaning; repository and ecosystem evidence decide spelling.

Use this evidence order:

1. User and repository instructions.
2. Project style guides and architecture decisions.
3. Formatter, linter, compiler, analyzer, and generator configuration.
4. Stable patterns in the same package, layer, or schema.
5. Framework, standard-library, and language conventions.
6. The closest skill profile only when it genuinely applies.

Discover casing, visibility, acronym handling, predicates, receivers, iterators, type parameters, async/effect conventions, public labels, framework magic, and interop constraints. Do not infer a repository-wide rule from one file.

First describe the semantic payload without syntax; then render it for the concrete role. Cross-layer spellings may differ while their concept remains continuous. Treat wire, ABI, database, CLI, infrastructure, reflection, and generated spellings as contracts.

Profiles are exception cards, not an allowlist. For an unlisted language, use local evidence, authoritative tooling, and a conservative no-op. Never import a convention because another language looks similar.
