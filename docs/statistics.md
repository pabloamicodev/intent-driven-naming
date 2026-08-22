# Statistical evaluation protocol

The primary estimand is generalized performance over software naming tasks similar to the declared case population; the unit of analysis is the evaluation case. The observed corpus mean is fixed-benchmark performance and MUST be reported as such when representativeness assumptions are not defensible.

Release conclusions use paired observations from identical cases, model configuration, and
replicate IDs. Current-skill quality is compared with the no-skill control; efficiency is compared
with a frozen previous-skill runtime. Mixing model versions, reasoning settings, adapter versions,
or grader policies within a system invalidates the comparison. The release gate requires at least three distinct pinned systems and rejects aliases that resolve to an identical configuration.

Efficiency gates use paired configurations and compare mean input tokens, output tokens, latency,
loaded skill words, turns, and tool calls with the frozen previous skill. Zero-versus-zero usage is
treated as no regression; positive usage against a zero baseline fails because no finite ratio can
justify it. Ratios are operational release thresholds, not evidence of statistical significance, so
reports retain raw coverage and distributions rather than presenting one composite score.

Activation and invariant proportions include Wilson 95% intervals. Paired quality deltas use a
deterministic 10,000-sample percentile bootstrap with a published seed. The bootstrap resamples
case clusters and keeps all replicates and invariants from each sampled case together. This avoids
treating correlated invariants or repeated runs of one task as independent evidence. It reports the
mean with-skill minus without-skill delta, cluster count, matched-pair count, wins, losses, and ties;
a p-value alone is insufficient.

The release gate also requires minimum per-slice results. Small slices are diagnostic and must not
be advertised as standalone proof. Adding many slices increases false-discovery risk, so post-hoc
slice findings are hypotheses until reproduced on held-out data. Failed, skipped, retried, and
ungraded cases remain visible; only the highest declared retry attempt is scored, and completeness
is checked per replicate.

Human semantic grades require at least two independent blinded human reviews, evidence for every label,
raw agreement, chance-corrected agreement, and decision-set agreement. Pairwise preference uses a
separate blinded orientation and private randomization salt. Critical contract or behavior failures
cannot be compensated by aggregate improvements.

External release evidence must publish the verified preregistration hash, dataset version, case exclusions, preregistered policy,
systems, configuration hashes, replicate count, usage coverage, intervals, reviewer agreement, and
all gate violations. The offline suite alone cannot establish cross-model effectiveness.

`specification/corpus-policy.json` prevents a maintenance change from silently shrinking the
balanced activation set, risk and decision coverage, language diversity, generation coverage, or
executable fixture floor. Raising those floors requires reviewed corpus evidence; lowering one
requires an explicit policy change visible in the diff.
