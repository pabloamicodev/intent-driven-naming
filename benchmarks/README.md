# Benchmarking

Benchmarks compare exact skill and agent configurations on versioned datasets. Lower token use, latency, or cost counts as an improvement only when safety and semantic gates continue to pass.

## Required Variants

- Candidate agent without the skill.
- The same agent with the released skill.
- Previous released skill when evaluating an instruction change.

Keep model, reasoning, tools, environment, retry policy, and case ordering equivalent across variants.

## Required Reports

- Activation precision, recall, and accuracy.
- Behavior pass rate and ungraded count.
- Critical contract failures.
- Results by language, mode, risk, and expected decision.
- Pairwise expert or calibrated-grader preference.
- Input tokens, output tokens, latency, and cost when available.
- Skipped fixtures and missing tools.

## Hard Gates

- Zero critical behavior or contract failures.
- No unauthorized writes in audit cases.
- No migration represented as a behavior-preserving rename.
- No benchmark publication with missing configuration metadata.
- The with-skill variant meets the versioned activation and behavior thresholds.
- The with-skill variant does not regress against the otherwise equivalent without-skill control.

Use `harness/run_adapter.py` to collect raw outputs, `harness/prepare_review.py` to blind behavior results, `harness/merge_reviews.py` to aggregate independent labels, and `harness/score_results.py --require-complete --policy specification/release-policy.json` for release scoring. Store release evidence in a versioned subdirectory rather than overwriting prior runs.
