# Conformance Levels

Conformance is cumulative. A higher level includes every lower-level requirement. Passing one aggregate average cannot compensate for a critical safety failure.

## Level 0 — Package Validity

- Valid `SKILL.md` frontmatter and metadata.
- Every routed reference exists.
- No duplicate section blocks or unresolved placeholders.
- Machine-readable datasets parse and use unique identifiers.
- Documented evaluation counts match the datasets.

## Level 1 — Routing and Scope

- Activation precision and recall are measured on positive, negative, borderline, multilingual, and noisy prompts.
- The released policy's activation thresholds pass for the with-skill variant without regressing against an equivalent without-skill control.
- Audit requests remain read-only.
- Refactor requests do not imply contract migrations or unrelated redesign.
- Context routes remain within their declared word budgets.
- Current-skill context and end-to-end input usage meet the versioned efficiency gate against a frozen previous runtime.

## Level 2 — Semantic Decisions

- Behavior cases pass the observable rubric.
- The released policy's behavior threshold passes with no ungraded invariants and no control regression.
- The system distinguishes `keep`, `rename`, `map`, `migrate`, and `defer`.
- Clear code and conventional short locals can produce a no-op.
- Language profiles render one semantic concept idiomatically rather than forcing uniform casing.
- Automated or model grading is calibrated against expert human labels.

## Level 3 — Refactor Safety

- Executable fixtures verify runtime behavior and protected output shapes.
- Public APIs, keyword parameters, serialization keys, dynamic references, generated sources, ABI surfaces, and stateful infrastructure are represented in the corpus.
- Critical contract-safety fixtures pass at 100%.
- Every applied rename records the checks run and unresolved surfaces.
- Non-trivial changes conform to the semantic-record and rename-plan contracts.

## Level 4 — Organization-Grade Evidence

- A held-out dataset is maintained separately from development cases.
- A preregistered experiment freezes the estimand, dataset and runtime hashes, systems, repetitions, retries, exclusions, and analysis before results are inspected.
- Results are reported per language, mode, contract risk, and outcome rather than only as one average.
- Blind pairwise comparisons and human review are repeated across releases.
- Cross-model and cross-agent compatibility is measured on at least three distinct pinned configurations with no drift between variants or repetitions.
- At least two independent human experts review every semantic candidate and pairwise comparison; automated judges cannot satisfy this minimum.
- CI blocks regressions, benchmark artifacts are reproducible, and limitations are public.

The repository MUST NOT claim a level until its evidence artifact records the suite version, implementation version, environment, and results needed for that level.
