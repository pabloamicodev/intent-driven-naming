# Audit and Refactor Decisions

An audit gathers evidence; it is not permission to edit. An authorized refactor selects the smallest set that restores semantic integrity.

## Classify the Actual Risk

Use the evidence order in `naming-model.md`. A generic word is a finding only when its actual scope hides material meaning.

Classify the highest applicable impact:

| Category | Meaning |
|---|---|
| Dangerous | A wrong inference can cause a defect, security issue, or data corruption. |
| Misleading | The name asserts behavior, state, effect, or representation the code lacks. |
| Ambiguous | A distinction required in this scope is absent. |
| Inconsistent | One concept uses conflicting vocabulary, or one word denotes different concepts. |
| Cosmetic | Meaning is already clear; preserve by default. |

Confidence is `high` when behavior, types, and vocabulary agree, `medium` when one source is incomplete, and `low` when meanings remain plausible. Low-confidence changes `defer`. Classify risk as `internal`, `cross-module`, `external`, `dynamic`, `generated`, `stateful`, or `unknown`.

## Evaluate the Candidate

Build the semantic record, state the wrong read and cost, choose one decision, and compare semantic gain with contract risk, diff size, and verification cost. Propose at most two evidence-supported candidates. Audit a callable as one unit: contract, parameters, local flow, failures, returns, effects, and callers. Rank a lying declaration above cosmetic locals.

## Output

Lead with material findings. Default to one compact row per finding: location, wrong read, evidence, decision/proposal, confidence, risk, and unresolved surface. Expand the full record only when requested or required for a plan. A justified no-op is valid; never manufacture findings.
