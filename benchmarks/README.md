# Benchmarking

Benchmarks compare exact skill and agent configurations on versioned datasets. Lower token use, latency, or cost counts as an improvement only when safety and semantic gates continue to pass.

## Required Variants

- Candidate agent without the skill.
- The same agent with the released skill.
- Previous released skill when evaluating an instruction change.

Keep model, reasoning, tools, environment, retry policy, and case ordering equivalent across variants.

## Required Reports

- Activation precision, recall, specificity, false-positive rate, balanced accuracy, accuracy, confidence intervals, and difficulty/locale slices.
- Behavior invariant pass rate, case pass rate, decision exact-match rate, and ungraded count.
- Critical contract failures.
- Results by language, mode, risk, and expected decision.
- Pairwise expert or calibrated-grader preference.
- Raw and chance-corrected reviewer agreement plus decision-set agreement.
- Input tokens, output tokens, latency, routed skill-context words, turns, tool calls, resource paths, and cost when available.
- Skipped fixtures and missing tools.

## Hard Gates

- Zero critical behavior or contract failures.
- No unauthorized writes in audit cases.
- No migration represented as a behavior-preserving rename.
- No benchmark publication with missing configuration metadata.
- The with-skill variant meets the versioned activation and behavior thresholds.
- The with-skill variant does not regress against the otherwise equivalent without-skill control.
- The with-skill variant meets the versioned input-token, context-word, and turn ratios against a frozen previous-skill runtime.
- Accuracy and invariant-pass deltas are computed from matched case/replicate outcomes with a deterministic paired 10,000-sample bootstrap rather than treating variants as unrelated samples.
- Every system and variant has at least three complete, independently identified repetitions.
- At least three distinct pinned systems are present and no system changes configuration across variants or repetitions.
- Review evidence meets the versioned human-reviewer-count and agreement thresholds.
- A verified preregistered release-candidate manifest includes both public and held-out data.
- Every loaded skill resource is reported, belongs to the route graph, and includes the universal semantic core.

Use `harness/run_experiment.py` to validate and execute the frozen matrix, then `harness/verify_experiment.py` to audit the evidence ledger. Use `harness/prepare_review.py` to blind behavior results, `harness/merge_reviews.py` to aggregate independent labels and calculate agreement, and the pairwise tools to measure direct preference. Run `harness/score_results.py --require-complete --policy specification/release-policy.json --review-agreement ... --experiment-verification ...` for release scoring. Store raw results, the exact runtime hashes, blinded-packet hashes, private-key custody notes, review records, configuration metadata, and final reports in a versioned evidence directory rather than overwriting prior runs. Follow the [external evaluation operations](../docs/external-evaluation.md), [statistics protocol](../docs/statistics.md), and [private-suite protocol](../docs/private-evaluation.md).
