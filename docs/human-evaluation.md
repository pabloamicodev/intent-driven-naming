# Human Evaluation Protocol

Human review calibrates semantic graders and validates that the project measures useful naming decisions rather than rubric wording.

## Sampling

Use a stratified sample across language, mode, identifier scope, contract risk, and expected outcome. Include typical, edge, adversarial, multilingual, typo-heavy, and minimal-context requests. Keep a held-out portion unavailable to ordinary instruction tuning.

## Review Design

- Randomize and blind implementation names.
- Reverse pairwise order across reviewers to detect position bias.
- Control gross output-length differences where verbosity is not the target.
- Give reviewers the prompt, relevant repository context, protected contracts, and executable verification results.
- Ask for pass/fail on critical invariants before any preference score.

Use `harness/prepare_review.py` to replace run and variant identity with an opaque review ID. Give the packet to reviewers but retain the generated key with the benchmark operator. The packet deliberately omits provider identity, variant, run ID, usage, cost, expected decision labels, and candidate artifact path. Sanitized artifact contents may be embedded after their path and hash are validated against an explicit artifact root.

Use `harness/prepare_pairwise_review.py` for direct A/B preference. It pairs otherwise equivalent with-skill and without-skill results, derives a reproducible random orientation from a private salt, and emits a separate reidentification key. Do not reuse a public or guessable salt for release evidence.

## Rubric

Reviewers evaluate:

1. Semantic truth.
2. Contract and behavior preservation.
3. Language idiom.
4. Proportionality and no-op quality.
5. Vocabulary continuity.
6. Scope discipline and evidence.

Provide anchored examples for unacceptable, acceptable, and excellent outcomes. Do not use one unanchored numerical score.

## Calibration

At least two experienced reviewers should label every release candidate. Resolve calibration disagreements through evidence and record whether the rubric, case context, or reviewer interpretation caused the difference. Do not adjudicate held-out release labels until the independent agreement report has been frozen.

Report raw grade agreement, chance-corrected grade agreement, decision-set agreement, and raw pairwise agreement. A semantic grader may scale only after its invariant and pairwise decisions agree sufficiently with expert labels on held-out cases.

Use reviewer IDs that are stable within a study but do not expose unnecessary personal data. Every grade requires observable evidence, and every review records the decisions it observed without seeing the expected labels. `harness/merge_reviews.py` rejects duplicate labels from the same reviewer on the same candidate. It treats any critical failure as decisive, applies strict majority only to noncritical invariants, and leaves ties or insufficient labels ungraded so the hard gate cannot silently pass them.

## Release Evidence

Record reviewer roles without exposing unnecessary personal data, case IDs, blind ordering, disagreements, adjudications, grader configuration, and final per-slice results. Never tune against the held-out labels and then report them as an independent benchmark.
