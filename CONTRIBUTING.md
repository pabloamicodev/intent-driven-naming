# Contributing

Contributions should improve measured decisions, contract safety, language fidelity, or maintainability. More instructions are not automatically better.

## Development Requirements

- Python 3.11 or newer for the offline harness.
- No runtime Python dependencies outside the standard library.
- Optional language tools for strict fixtures: Node.js, Go, Rust, and Java.
- A private, access-controlled evidence location for held-out release runs.

Run the full offline suite:

```text
python scripts/run_checks.py
```

Regenerate machine-readable evaluations after editing their reviewed Markdown sources:

```text
python scripts/export_evals.py --write
```

## Change Types

### Instruction or Routing Changes

- Explain which observed failure or supported use case motivates the change.
- Put each rule in one authoritative location.
- Keep the entrypoint discriminating and route conditional detail progressively.
- Compare context-route measurements before and after the change.
- Add or update an evaluation that would fail without the change.

### Evaluation Changes

- Use realistic requests rather than wording tailored to the current instructions.
- State observable invariants, not an exact preferred answer.
- Mark behavior or contract preservation as critical when failure can break software.
- Include `keep`, `map`, `migrate`, and `defer` cases, not only successful renames.
- Keep held-out cases outside ordinary prompt tuning.

### Language Profile Changes

- Cite repository, language, framework, or standard-library evidence in the pull request.
- Preserve idiomatic exceptions and public contract rules.
- Add at least one positive case, one no-op or hard negative, and one contract-risk case.
- Request review from an engineer experienced in the affected ecosystem.

### Harness and Fixture Changes

- Keep the harness provider-neutral and credentials out of datasets.
- Use subprocess argument arrays rather than shell interpolation.
- Isolate generated candidates in temporary directories.
- Add unit tests and verify failure behavior, not only the passing path.

## Pull Request Evidence

Every material pull request should include:

- the problem and affected conformance level;
- relevant cases or fixtures;
- commands run and their results;
- context-budget impact;
- known limitations and unverified environments;
- whether the change affects activation behavior or public schemas.

Do not add forbidden-word linters that reject identifiers from spelling alone. Deterministic tooling may validate package structure, observable contracts, compiled behavior, generated datasets, and benchmark accounting.

## Release Process

1. Update `VERSION` and `CHANGELOG.md`.
2. Regenerate datasets and run all offline checks.
3. Run strict fixtures in CI.
4. Run the held-out benchmark matrix for material instruction changes.
5. Review critical failures and per-slice regressions.
6. Tag the release only after required evidence is attached.
7. Build the deterministic archive, checksum manifest, SPDX inventory, and provenance attestation from the tag workflow.
