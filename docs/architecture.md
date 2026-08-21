# Architecture

Intent-Driven Naming separates semantic judgment from deterministic verification.

## Loaded Skill Surface

`SKILL.md` selects one mode, relevant feature guidance, and the smallest applicable language surface. `naming-model.md` is the universal semantic core. Convention discovery is conditional when local evidence is already clear. Cross-ecosystem work uses the compact polyglot boundary protocol and at most two full profiles concurrently.

Only Markdown files routed for the current task become instructions. Specifications, datasets, fixtures, scripts, and governance files remain outside model context unless a maintenance task explicitly reads them.

## Engineering Surface

- `specification/` defines normative outcomes, schemas, routes, budgets, and adapter contracts.
- `evals/cases/` contains generated machine-readable datasets.
- `evals/fixtures/` contains executable contract examples.
- `harness/` runs adapters, prepares blinded reviews, aggregates independent labels, verifies fixtures, and scores graded results.
- `scripts/` validates and maintains the repository.
- `tests/` verifies the harness and generation logic.

## Trust Boundaries

The skill performs semantic judgment. Repository scripts do not reject names from spelling alone. Deterministic checks validate observable facts such as package integrity, duplicated content, compilation, output shapes, state migrations, and score accounting.

Non-trivial audits produce semantic records. Rename plans carry materiality, analysis coverage, explicit authorization and change budgets, protected spellings, unresolved surfaces, and verification or rollback obligations. The dependency-free runtime validator rejects cross-field safety violations; repository tools and language analyzers then verify project-specific behavior.

Structural discovery prefers symbol graphs, language servers, ASTs, compiler indexes, and reference search. Only the smallest evidence slice needed for a decision should enter model context. See the [data-handling policy](data-handling.md).

Agent and grader adapters are external trust boundaries. They communicate through JSONL, run without shell interpolation, and must be isolated by their host. Reported resources are checked against case mode, features, and language profiles so irrelevant references cannot hide inside aggregate token totals.

## Source of Truth

- Normative behavior: `specification/decision-model.md`.
- Agent instructions: `SKILL.md` and routed references.
- Human-reviewed cases: Markdown files under `evals/`.
- Machine-readable cases: generated JSONL under `evals/cases/`.
- Route composition and budgets: JSON under `specification/`.
- Release version: `VERSION` and `CHANGELOG.md`.
- Portable audit and rename contracts: `semantic-record.schema.json` and `rename-plan.schema.json`.
