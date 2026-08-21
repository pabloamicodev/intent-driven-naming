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

Agent and grader adapters are external trust boundaries. They communicate through JSONL, run without shell interpolation, and must be isolated by their host.

## Source of Truth

- Normative behavior: `specification/decision-model.md`.
- Agent instructions: `SKILL.md` and routed references.
- Human-reviewed cases: Markdown files under `evals/`.
- Machine-readable cases: generated JSONL under `evals/cases/`.
- Route composition and budgets: JSON under `specification/`.
- Release version: `VERSION` and `CHANGELOG.md`.
