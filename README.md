# Intent-Driven Naming

Version 1.1.0 is an Agent Skill and conformance project for generating, auditing, and safely refactoring software identifiers according to semantic intent across languages and development stacks.

The core skill remains instruction-only. Deterministic tooling surrounds it to validate the package, route context efficiently, execute contract fixtures, run provider-neutral evaluations, and block safety regressions. No script rejects an identifier merely because it is called `data`, `result`, `item`, `i`, or another generic or short name.

## What It Covers

- Functions, methods, constructors, commands, queries, predicates, handlers, and callbacks.
- Parameters, argument labels, local variables, captures, accumulators, errors, and intermediate results.
- Types, interfaces, schemas, queries, scripts, configuration, and infrastructure identifiers.
- New-code generation, read-only audit, targeted refactor, and protected-boundary mapping.
- Language idiom without forcing one ecosystem's casing or programming model onto another.

## Decision Outcomes

The normative model defines five outcomes:

| Outcome | Use |
|---|---|
| `keep` | The current name is clear, conventional, contract-bound, or not worth the churn. |
| `rename` | A supported internal rename creates material semantic gain. |
| `map` | Preserve an external spelling and expose a clearer internal alias. |
| `migrate` | Treat a public, persisted, dynamic, or stateful change as a coordinated migration. |
| `defer` | Available evidence cannot establish meaning or safety. |

Behavior regressions, silent contract changes, invented domain meaning, unauthorized audit mutations, and migrations disguised as refactors are non-compensable failures.

## Architecture

```text
intent-driven-naming/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── naming-model.md
│   ├── language-conventions.md
│   ├── polyglot-boundaries.md
│   ├── new-code-workflow.md
│   ├── audit-and-refactor.md
│   ├── refactor-safety.md
│   ├── callable-naming.md
│   ├── local-variable-naming.md
│   ├── typescript-javascript.md
│   ├── web-frameworks.md
│   └── language-family profiles
├── specification/
│   ├── decision-model.md
│   ├── conformance-levels.md
│   ├── adapter-protocol.md
│   ├── routes.json
│   └── JSON schemas and context budgets
├── evals/
│   ├── trigger-cases.md
│   ├── behavior-cases.md
│   ├── cases/
│   │   ├── activation.jsonl
│   │   └── behavior.jsonl
│   └── fixtures/
├── harness/
├── scripts/
├── tests/
├── docs/
└── .github/workflows/ci.yml
```

`SKILL.md` remains the small router. The semantic core is always loaded; workflows, callable guidance, local-variable guidance, convention discovery, and language profiles are conditional. Specifications, datasets, fixtures, and maintenance scripts stay outside normal task context.

This follows the progressive-disclosure design described in the [official OpenAI documentation for Skills](https://learn.chatgpt.com/docs/build-skills).

## Install as a Skill

Install the runtime-only surface from this checkout:

```powershell
python scripts/install_local_skill.py --destination "$HOME/.codex/skills/intent-driven-naming"
python scripts/install_local_skill.py --destination "$HOME/.codex/skills/intent-driven-naming" --check
```

The installer refuses to overwrite an existing destination. For a repository-scoped installation, place the runtime surface so the entrypoint is available at one of these locations:

```text
$HOME/.agents/skills/intent-driven-naming/SKILL.md
$HOME/.codex/skills/intent-driven-naming/SKILL.md
$REPOSITORY_ROOT/.agents/skills/intent-driven-naming/SKILL.md
```

The skill itself has no runtime dependency. Python is required only for repository validation and evaluation tooling.

## Use

Generate new code:

```text
$intent-driven-naming Implement a checkout service with clear names for requests, totals, payment state, and errors.
```

Run a read-only audit:

```text
$intent-driven-naming Audit identifiers in this module. Rank material findings and do not edit files.
```

Apply a safe refactor:

```text
$intent-driven-naming Rename dangerous or misleading identifiers without changing behavior or external contracts.
```

## Language and Development Coverage

| Profile | Representative coverage |
|---|---|
| TypeScript and JavaScript | Node.js, browser modules, types, async APIs, serialization |
| Web frameworks | React, React Query, Vue, Svelte, Angular |
| Dynamic languages | Python, Ruby, PHP |
| Systems languages | Go, Rust, C, C++ |
| Managed and mobile | Java, Kotlin, C#, Swift, Dart |
| Functional and concurrent | Haskell, OCaml, F#, Scala, Clojure, Erlang, Elixir |
| Data and infrastructure | SQL, schemas, pipelines, shell, PowerShell, Terraform, Kubernetes |

Profiles are refinements, not an allowlist. Unlisted languages use the semantic model, repository evidence, compiler or analyzer feedback, and conservative contract safety.

See [compatibility](docs/compatibility.md) for evidence-scoped support claims and [limitations](docs/limitations.md) for what is not yet proven.

## Offline Validation

Run every repository, unit, dataset, and fixture check:

```text
python scripts/run_checks.py
```

Individual commands:

```text
python scripts/export_evals.py --check
python scripts/validate_repository.py
python -m unittest discover -s tests -v
python harness/verify_fixtures.py
```

Install `requirements-dev.lock` when running the same strict JSON Schema and lint checks enforced by CI. The skill runtime itself still has no Python dependency.

The repository contains 60 balanced activation cases, 36 behavior cases with 137 explicit invariants, and 11 executable or contract-verifiable fixtures across JavaScript, TypeScript, Python, Go, Rust, Java, C#, SQL, Terraform, dynamic lookup, and generated code. Activation requests span five locales, and behavior cases include English, Spanish, and Portuguese prompts.

Generated JSONL remains synchronized with the reviewed Markdown source:

```text
python scripts/export_evals.py --write
```

## Provider-Neutral Evaluation

Candidate and grader integrations communicate through JSONL instead of a vendor SDK. Run an adapter without shell interpolation:

```text
python harness/run_adapter.py \
  --cases evals/cases/activation.jsonl \
  --output eval-results/activation.jsonl \
  --variant with-skill \
  --system-id your-agent-model-config \
  --replicate-id r1 \
  -- your-adapter-command
```

The included Codex CLI adapter can be used as the adapter command. Pin the model version in the benchmark record rather than inferring it later:

```text
python harness/run_adapter.py \
  --cases evals/cases/activation.jsonl \
  --output eval-results/codex-with-skill-r1.jsonl \
  --variant with-skill \
  --system-id codex-model-high \
  --replicate-id r1 \
  -- python adapters/codex_cli.py \
     --model MODEL_ID \
     --model-version PINNED_MODEL_VERSION \
     --reasoning high \
     --artifact-output-root eval-results/artifacts
```

Repeat the same command for `without-skill` and for `r1`, `r2`, and `r3`, changing only the variant or replicate identity.

Create blinded review packets for behavior results. Keep the reidentification key private from reviewers:

```text
python harness/prepare_review.py \
  --results eval-results/behavior.jsonl \
  --artifact-root eval-results/artifacts \
  --packet-output eval-results/review-packets.jsonl \
  --key-output eval-results/review-keys.jsonl
```

After independent reviewers return records matching `specification/review-record.schema.json`, merge their labels and score the complete run:

```text
python harness/merge_reviews.py \
  --results eval-results/behavior.jsonl \
  --review-keys eval-results/review-keys.jsonl \
  --reviews eval-results/reviews.jsonl \
  --minimum-reviews 2 \
  --agreement-output eval-results/review-agreement.json \
  --output eval-results/graded-behavior.jsonl

python harness/prepare_pairwise_review.py \
  --results eval-results/behavior-with.jsonl eval-results/behavior-without.jsonl \
  --artifact-root eval-results/artifacts \
  --salt STUDY_SECRET \
  --packet-output eval-results/pairwise-packets.jsonl \
  --key-output eval-results/pairwise-keys.jsonl

python harness/score_pairwise.py \
  --keys eval-results/pairwise-keys.jsonl \
  --reviews eval-results/pairwise-reviews.jsonl \
  --minimum-reviews 2 \
  --output eval-results/pairwise-report.json

python harness/score_results.py \
  --results eval-results/activation.jsonl eval-results/graded-behavior.jsonl \
  --require-complete \
  --policy specification/release-policy.json \
  --review-agreement eval-results/review-agreement.json \
  --pairwise-report eval-results/pairwise-report.json \
  --json-output benchmark-results/report.json \
  --markdown-output benchmark-results/report.md
```

For exploratory partial runs, omit `--require-complete` and `--policy`. Release evidence MUST use both. The policy requires three complete repetitions of with-skill and without-skill cohorts, pinned implementation metadata, at least 0.90 activation precision, recall, specificity, balanced accuracy, and overall accuracy, at least 0.90 invariant pass rate, at least 0.85 case and decision accuracy, calibrated reviewer agreement, no ungraded invariants, and no material regression against the control. Critical failures, duplicate attempts, malformed identities, incomplete repetitions, and unresolved review labels fail the release gate.

Reports separate activation, behavior, completion, confidence intervals, retries, critical failures, decision accuracy, reviewer agreement, and difficulty, locale, language, mode, risk, and expected-decision slices. A critical failure makes the hard gate fail regardless of aggregate quality.

The evaluation design follows the [official OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): task-specific cases, automated scoring where appropriate, continuous evaluation, typical and adversarial inputs, and human calibration of model graders.

## Conformance and Evidence

The project defines four cumulative evidence levels beyond package validity:

1. Routing and scope.
2. Semantic decisions.
3. Refactor safety.
4. Organization-grade held-out, human-calibrated, cross-agent evidence.

The offline repository can prove package validity and executable fixture safety. Level 4 cannot be claimed without external model runs, pinned configurations, held-out data, and expert review. See the [release policy](specification/release-policy.json), [conformance levels](specification/conformance-levels.md), [human evaluation](docs/human-evaluation.md), and [benchmarking](benchmarks/README.md).

## Contributing and Governance

- [Contributing](CONTRIBUTING.md)
- [Governance](GOVERNANCE.md)
- [Security policy](SECURITY.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md)

The project is licensed under Apache License 2.0. See [LICENSE](LICENSE).
