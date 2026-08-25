# Changelog

All notable changes are documented here. The project follows Semantic Versioning.

## Unreleased

### Changed

- Moved the skill's runtime surface (`SKILL.md`, `references/`, `scripts/runtime/`, `agents/openai.yaml`, and the `rename-plan`/`semantic-record` schemas) from the repository root into `skills/intent-driven-naming/`, so third-party installers that discover a skill by its containing directory (e.g. `npx skills add`) install only the skill instead of the whole repository. `README.md` documents the new `npx skills add pabloamicodev/intent-driven-naming` install path alongside the existing hash-verified Python installer.
- `scripts/compare_context.py --baseline-ref <ref>` no longer resolves against any ref predating this restructuring commit, since those refs still have `SKILL.md` at the repository root; comparisons must use a baseline ref at or after this change.

## 2.0.0 — 2026-08-21

### Added

- A compact semantic decision kernel with explicit wrong-read analysis and high-risk guidance for security, distributed systems, time, data/ML, observability, and resource semantics.
- Portable semantic-record and rename-plan schemas plus a dependency-free runtime safety validator.
- Structural-analysis guidance for symbol graphs, language servers, ASTs, compiler indexes, dynamic strings, and minimal evidence collection.
- A three-cohort evaluation protocol: current skill versus no-skill for quality and frozen previous skill for efficiency.
- Resource-loading telemetry, context-word, token, latency, turn, and tool-call coverage gates; deterministic paired bootstrap intervals; and a documented statistical protocol.
- Sixteen behavior cases and twenty-four balanced activation cases across additional locales and high-risk domains, raising the corpus to 84 activation cases and 52 behavior cases with 202 invariants.
- Security trust-stage, partial-guarantee, shell process-contract, generated Protobuf mapping, and telemetry fixtures, raising executable coverage to 16 fixtures.
- Private held-out-suite validation, data-minimization guidance, deterministic release archives, checksums, SPDX inventory, and atomic installation replacement with backup.
- Materiality, structural-coverage, collision, dynamic-surface, change-budget, and rollback invariants in portable rename plans.
- Corpus regression policy, schema-to-runtime parity tests, clustered paired intervals, package manifests, and high-confidence secret scanning for review artifacts.
- Bounded adapter input, stdout, and stderr handling with disk-backed streams instead of unbounded memory capture.
- Preregistered experiment manifests, shell-free matrix execution, resumable evidence ledgers, independent evidence verification, and explicit generalized-performance estimands.
- Organization gates for three distinct pinned systems, configuration stability across variants and repetitions, held-out evidence, and two human reviews per candidate and pair.
- Progressive evidence acquisition with explicit stop conditions for lower token use and proprietary-source disclosure.
- Declaration-family guidance for types, fields, collections, enums, constants, errors, events, messages, type parameters, modules, and namespaces.
- All-path semantic guarantees, adversarial behavior cases, and an executable partial-validation fixture.
- Exact UTF-8 instruction-data budgets and release gates for output-token, latency, and tool-call regressions.

### Changed

- Reduced entrypoint, reference, standard-route, and extended-route context budgets substantially.
- Upgraded release, audit, semantic, and efficiency contracts to version 2.0.
- Made generated-code risk explicit and required unresolved contract surfaces to block a changing plan.
- Moved installation backups outside one-level skill discovery paths to prevent duplicate activation.
- Lowered the entrypoint, always-loaded, route, and total runtime budgets while adding the declaration capability.

## 1.1.0 — 2026-08-21

### Added

- Balanced, versioned activation data with 60 cases, multilingual boundaries, adversarial negatives, explicit strata, content hashes, and a generated manifest.
- Explicit metadata for 36 behavior cases across three locales, covering mode, language, difficulty, contract risk, expected decision, invariant severity, and grading method.
- Repeated-run and multi-system evaluation identities, specificity and balanced-accuracy metrics, Wilson intervals, decision confusion, retry accounting, and per-slice reports.
- Sanitized artifact bundles, evidence-required independent review, reviewer-agreement statistics, and blinded randomized pairwise comparison.
- A reference Codex CLI adapter that isolates cases and keeps with-skill and without-skill workspaces configuration-equivalent.
- A compact polyglot boundary protocol for mapping internal, external, generated, dynamic, and persisted identifiers.
- Executable TypeScript serialization, Python runtime-registry, C# named-argument, and generated-source fixtures.
- JSON Schema validation, pinned CI actions and development dependencies, and a deterministic runtime-only local installer.

### Changed

- Tightened activation scope so explicit identifier-preservation and behavior-only tasks do not activate the skill.
- Raised the organization release contract to dataset and policy version 1.1 with three required replicates, control comparisons, reviewer agreement, decision accuracy, false-positive, and critical-safety gates.
- Limited polyglot context to a boundary map and at most two simultaneous full language profiles.

## 1.0.0 — 2026-08-21

### Added

- Normative decision specification with `keep`, `rename`, `map`, `migrate`, and `defer` outcomes.
- Machine-readable activation and behavior datasets derived from the reviewed Markdown cases.
- Provider-neutral JSONL adapter protocol, runner, scoring harness, and hard safety gates.
- Blinded independent-review packets and conservative multi-reviewer grade aggregation.
- A versioned release policy with activation, semantic-quality, control-regression, completeness, and reproducibility gates.
- Usage, latency, cost, completion, and tag-slice reporting when adapters provide the underlying observations.
- Executable contract fixtures for JavaScript, Python, Go, Rust, Java, SQL, and Terraform.
- Repository validation for routes, context budgets, links, duplicate content, metadata, datasets, and governance.
- CI, contribution, governance, security, conduct, compatibility, and benchmarking documentation.

### Changed

- Split callable declaration guidance from local-variable guidance.
- Split TypeScript/JavaScript guidance from component-framework guidance.
- Made language-convention discovery conditional when local conventions are already authoritative and clear.
- Established explicit context budgets for entrypoint, references, and composed routes.
- Made incomplete runs and ungraded critical invariants fail release scoring.
- Hardened external adapter handling against identity spoofing, malformed records, unknown fields, and oversized output.

### Fixed

- Removed duplicated and corrupted sections from the TypeScript/JavaScript profile.

## 0.3.0 — 2026-08-21

- Added function, parameter, and local-variable naming guidance.

## 0.2.0 — 2026-08-21

- Expanded the skill across language families, schemas, data, shell, and infrastructure.

## 0.1.0 — 2026-08-21

- Created the initial Intent-Driven Naming skill.
