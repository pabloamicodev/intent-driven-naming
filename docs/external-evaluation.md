# External Evaluation Operations

External effectiveness is an evidence claim, not a property that can be established by repository tests alone. The repository therefore makes the experiment reproducible, auditable, and difficult to misconfigure before any paid model call is made.

## Evidence Ladder

1. Run the offline suite on every change. It proves package, schema, harness, routing, and fixture integrity.
2. Run a low-cost development experiment on public cases. It detects integration and gross quality failures but cannot support an organization-grade claim.
3. Freeze a release-candidate manifest before looking at results. It must identify at least three distinct pinned systems, the controlled variants, replicate IDs, the exact runtimes and policy, a public suite, and an access-controlled held-out suite.
4. Execute the full Cartesian matrix, preserve raw outputs, and verify its evidence ledger.
5. Conduct blinded invariant and pairwise review with at least two human experts per candidate or pair. Model graders may assist but cannot satisfy the human-review minimum.
6. Score the complete reviewed evidence with the frozen policy and publish failures, exclusions, uncertainty, and limits alongside successes.

This staged design saves external tokens and reviewer time because an experiment advances only after cheaper deterministic and public-data checks pass. Release evidence still uses the full preregistered matrix; screening results are never substituted for it.

## Freeze the Experiment

Start from `examples/experiment-manifest.json` and `examples/runner-config.json`. The manifest is shareable evidence. It contains only identities, analysis choices, counts, and SHA-256 digests. The runner configuration is operator-local: it maps those frozen identities to dataset paths and shell-free adapter command arrays. After editing the study design and local mappings, calculate every dataset, runtime, and policy identity atomically:

Runtime identities cover only the declared source formats in the installable surface. Generated caches, bytecode, logs, and unrelated working-tree files are excluded, so running validation cannot silently change the frozen identity or release archive.

```text
python harness/freeze_experiment.py \
  --draft path/to/experiment-draft.json \
  --runner-config path/to/runner-config.json \
  --output path/to/experiment-manifest.json
```

The command refuses to replace an existing manifest unless `--replace` is explicit. Commit or otherwise timestamp the frozen manifest before executing the first model call.

For `purpose: release-candidate`:

- Include at least one `visibility: held-out` dataset whose cases were not used to tune the skill.
- Pin at least the number of distinct systems and replicates required by `specification/release-policy.json`.
- Use distinct actual model or agent configurations; aliases for one configuration are rejected.
- Pin sampling, tool, reasoning, and other consequential settings as scalar fields in each `implementation` object.
- Keep exclusions and allowable retry reasons fixed before the first result is examined.

Validate the manifest, local paths, hashes, configuration uniqueness, and complete job count without making an external call:

```text
python harness/run_experiment.py \
  --manifest path/to/experiment-manifest.json \
  --runner-config path/to/runner-config.json
```

The scorer estimates generalized task performance by resampling case clusters. The manifest therefore names the target population explicitly rather than presenting the observed benchmark mean as universal performance. A different estimand requires a separately reviewed analysis plan.

## Execute and Resume

Execution is explicit because adapters may incur cost:

```text
python harness/run_experiment.py \
  --manifest path/to/experiment-manifest.json \
  --runner-config path/to/runner-config.json \
  --execute
```

The runner invokes commands as argument arrays without a shell, inherits credentials from the host environment, uses bounded adapter I/O, and writes one immutable result file per dataset, suite, system, variant, and replicate. It never records credentials or adapter commands in the public evidence ledger.

If a process stops, use `--resume`. Existing files are reused only after every case identity, dataset version, configuration hash, implementation field, and output order matches the frozen experiment. Retrying a failed job additionally requires `--retry-reason` with one of the reasons frozen in the manifest; the runner increments the result attempt, preserves prior ledger history, and enforces the preregistered attempt limit. Invalid or ambiguous evidence is not overwritten automatically.

After completion, independently verify the ledger and raw results:

```text
python harness/verify_experiment.py \
  --manifest path/to/experiment-manifest.json \
  --runner-config path/to/runner-config.json \
  --experiment-root path/to/results/EXPERIMENT_ID \
  --json-output path/to/experiment-verification.json
```

## Review and Promotion

Prepare blind packets only after raw evidence is frozen. Human reviewers use pseudonymous stable IDs and declare `reviewer_kind: human`. Candidate identity, provider, variant, expected decision, usage, and review keys remain hidden. At least two humans review every candidate and every A/B pair; disagreements remain unresolved until a genuine majority exists. Critical failures are never outvoted by style preferences.

The final scoring command includes the experiment verification report:

```text
python harness/score_results.py \
  --results path/to/all-reviewed-results.jsonl \
  --require-complete \
  --policy specification/release-policy.json \
  --review-agreement path/to/review-agreement.json \
  --pairwise-report path/to/pairwise-report.json \
  --experiment-verification path/to/experiment-verification.json \
  --json-output path/to/final-report.json \
  --markdown-output path/to/final-report.md
```

The gate fails when preregistration is absent, a held-out suite is absent, systems are insufficient or duplicated, a configuration changes between variants or repetitions, human coverage is insufficient, evidence is incomplete, or any existing semantic, contract, routing, or efficiency threshold fails.

## Interpretation

Passing supports only the population, systems, versions, datasets, and conditions named in the experiment. It does not prove that every language, repository, model, or future version benefits. Report the observed benchmark performance and the generalized-task estimand separately, disclose the case-sampling assumptions, and repeat the study for materially different agent families or task populations.

The design follows current primary guidance emphasizing frozen configurations, task-specific evaluation, uncertainty, transparent reporting, and explicit estimands: the [OpenAI evaluation guide](https://developers.openai.com/api/docs/guides/evaluation-best-practices), the draft [NIST AI 800-2 automated benchmark practices](https://www.nist.gov/news-events/news/2026/01/towards-best-practices-automated-benchmark-evaluations), and [NIST AI 800-3 on benchmark versus generalized performance](https://www.nist.gov/publications/expanding-ai-evaluation-toolbox-statistical-models).
