# Audit and Refactor Decisions

An audit gathers evidence; it is not permission to edit. For an authorized refactor, select the smallest change set that restores semantic integrity.

## Establish Truth Before Judging Spelling

Inspect declarations, types, assignments, transformations, callers, consumers, effects, failures, tests, schemas, runtime registrations, and domain vocabulary. A generic word is a finding only when its actual scope hides material meaning.

Classify the highest applicable impact:

| Category | Meaning |
|---|---|
| Dangerous | A wrong inference can cause a defect, security issue, or data corruption. |
| Misleading | The name asserts behavior, state, or representation the code does not have. |
| Ambiguous | A distinction required in this scope is absent. |
| Inconsistent | One concept uses conflicting vocabulary, or one word denotes different concepts. |
| Cosmetic | Meaning is already clear; preserve by default. |

Confidence is `high` when behavior, types, and vocabulary agree; `medium` when one source is incomplete; and `low` when multiple meanings remain plausible. Low-confidence, high-risk cases should normally `defer`.

Contract risk is `internal`, `cross-module`, `external`, `dynamic`, `generated`, `stateful`, or `unknown`. A local declaration can still expose its spelling through named arguments, shorthand output, reflection, templates, captures, macros, or generated code.

## Evaluate the Candidate

1. Build the semantic record.
2. State the plausible wrong reading and its impact.
3. Choose `keep`, `rename`, `map`, `migrate`, or `defer`.
4. For a change, propose at most two evidence-supported candidates.
5. Remove redundant words and check vocabulary families.
6. Compare semantic gain with contract risk, diff size, and verification cost.

Audit callables as one unit: observable contract, parameters, local flow, errors, returns, side effects, and callers. Rank a lying declaration above cosmetic local issues.

## Output

Lead with material findings. For several findings use: location, current name, impact, evidence, decision, proposed name, confidence, and contract risk. Identify protected spellings and unresolved vocabulary decisions. A justified no-op is a valid result; never manufacture findings.
