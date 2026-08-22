# Intent-Driven Naming 2.0.0 Offline Evidence

This directory records repository-owned checks for version `2.0.0`. It is offline engineering
evidence, not a claim that external model, cross-provider, private held-out, or expert-review gates
have passed.

Machine-readable evidence is recorded in [context comparison](context-comparison.json), [schema
validation](schema-validation.json), and [repository validation](repository-validation.json).

## Static context result

`context-comparison.json` compares this worktree with immutable baseline commit
`44fe691f9cc7e3182df1cb0da947ea9ca206cf8e` using whitespace-delimited words and the route
composition algorithm enforced by the repository validator.

| Measure | 1.1.0 baseline | 2.0.0 candidate | Reduction |
|---|---:|---:|---:|
| Entrypoint | 836 | 409 | 51.1% |
| Always-loaded route | 2,195 | 979 | 55.4% |
| All runtime instructions | 12,828 | 4,062 | 68.3% |
| Maximum standard route | 6,850 | 2,834 | 58.6% |
| Maximum extended route | 9,035 | 3,286 | 63.6% |

These are deterministic context-size measures, not provider token counts. Release evaluation must
also record provider-reported input tokens and compare the current skill against a frozen previous
runtime under the same cases and model configuration.

## Offline coverage

- 84 activation cases, exactly 42 positive and 42 negative, across seven locales.
- 48 behavior cases with 185 typed invariants across generation, audit, and refactor modes.
- 15 fixtures covering runtime, compile-time, serialized, dynamic, generated, stateful, shell,
  security, Protobuf, and observability boundaries.
- Portable semantic records and rename plans checked by JSON Schema and a dependency-free runtime
  validator, including materiality, collision, coverage, scope-budget, and rollback invariants.
- Deterministic release archive, internal file manifest, SHA-256 sums, SPDX file inventory, and tag
  provenance workflow.
- Case-clustered paired intervals, corpus regression floors, exact resource-route gates, and
  high-confidence secret rejection for review artifacts.
- Preregistered experiment freezing, shell-free matrix execution, resumable immutable outputs,
  evidence-ledger verification, and cryptographic linkage from scored runs to the experiment.
- Human-first consensus: automated graders can contribute evidence but cannot outvote experts or
  satisfy the two-human minimum.

## Evidence still required before a release claim

- A preregistered release-candidate experiment with public and private held-out suites.
- Three complete current-skill, previous-skill, and no-skill repetitions on at least three distinct
  pinned agent/model identities, without configuration drift.
- At least two independent human reviews for every semantic candidate and pairwise comparison,
  meeting the agreement policy.
- Published configuration hashes, raw-result custody, usage coverage, statistical intervals, and
  every gate violation.

No release tag should be created until those external requirements pass. Offline checks may merge
as a release candidate without representing organization-grade effectiveness.
