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
| Always-loaded route | 2,195 | 956 | 56.4% |
| All runtime instructions | 12,828 | 4,067 | 68.3% |
| Maximum standard route | 6,850 | 2,839 | 58.6% |
| Maximum extended route | 9,035 | 3,291 | 63.6% |

These are deterministic context-size measures, not provider token counts. Release evaluation must
also record provider-reported input tokens and compare the current skill against a frozen previous
runtime under the same cases and model configuration.

## Offline coverage

- 84 activation cases, exactly 42 positive and 42 negative, across seven locales.
- 48 behavior cases with 185 typed invariants across generation, audit, and refactor modes.
- 15 fixtures covering runtime, compile-time, serialized, dynamic, generated, stateful, shell,
  security, Protobuf, and observability boundaries.
- Portable semantic records and rename plans checked by JSON Schema and a dependency-free runtime
  validator.
- Deterministic release archive, SHA-256 manifest, SPDX file inventory, and tag provenance workflow.

## Evidence still required before a release claim

- Three complete current-skill, previous-skill, and no-skill repetitions for every declared system.
- Independent blinded semantic review and pairwise comparison meeting the release policy.
- A frozen private held-out suite validated outside the repository.
- Published configuration hashes, raw-result custody, usage coverage, statistical intervals, and
  every gate violation.

No release tag should be created until those external requirements pass. Offline checks may merge
as a release candidate without representing organization-grade effectiveness.
