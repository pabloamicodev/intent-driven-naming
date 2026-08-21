# Audit and Refactor Decisions

An audit gathers evidence; it is not permission to edit. For an authorized refactor, select the smallest change set that restores semantic integrity.

## Classify the Actual Risk

Use the evidence order in `naming-model.md`. A generic word is a finding only when its actual scope hides material meaning.

Classify the highest applicable impact:

| Category | Meaning |
|---|---|
| Dangerous | A wrong inference can cause a defect, security issue, or data corruption. |
| Misleading | The name asserts behavior, state, or representation the code does not have. |
| Ambiguous | A distinction required in this scope is absent. |
| Inconsistent | One concept uses conflicting vocabulary, or one word denotes different concepts. |
| Cosmetic | Meaning is already clear; preserve by default. |

Confidence is `high` when behavior, types, and vocabulary agree, `medium` when one source is incomplete, and `low` when meanings remain plausible. Low-confidence changes `defer`. Classify contract risk as `internal`, `cross-module`, `external`, `dynamic`, `generated`, `stateful`, or `unknown`.

## Evaluate the Candidate

1. Build the semantic record.
2. State the plausible wrong read and classify its cost as `none`, `low`, `material`, or `critical`.
3. Choose `keep`, `rename`, `map`, `migrate`, or `defer`; change only material or critical cases.
4. Propose at most two supported candidates, remove redundancy, and check vocabulary families.
5. Compare semantic gain with contract risk, diff size, and verification cost.

Audit callables as one unit: observable contract, parameters, local flow, errors, returns, side effects, and callers. Rank a lying declaration above cosmetic local issues.

## Output

Lead with material findings. For several, report location, name, materiality, evidence, decision, proposal, confidence, risk, protected spellings, and unresolved decisions. A justified no-op is valid; never manufacture findings.
