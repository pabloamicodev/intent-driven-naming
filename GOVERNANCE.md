# Governance

The project is governed by evidence, review, and transparent release criteria rather than by the volume of instructions added.

## Roles

- Maintainers merge changes, publish releases, and enforce conformance gates.
- Language stewards review idiom and contract behavior for ecosystems they know deeply.
- Evaluation reviewers maintain rubrics, held-out cases, and human-label calibration.
- Contributors may propose changes through the same evidence requirements regardless of affiliation.

Roles are earned through sustained, high-quality contributions. Repository hosting organizations should record current maintainers and language stewards in their native ownership controls.

## Decision Process

Routine changes require passing CI and maintainer review. Changes to normative outcomes, hard gates, schemas, licensing, or conformance definitions require:

1. A written rationale and alternatives considered.
2. A compatibility and migration assessment.
3. Evaluation evidence on affected slices.
4. Approval from at least two maintainers when the project has enough active maintainers.

When consensus is unavailable, maintainers should prefer a reversible experiment, retain the current stable behavior, or document the disagreement rather than silently broadening the specification.

## Language Stewardship

No single maintainer should declare an ecosystem idiom authoritative without relevant experience or primary evidence. A language profile is eligible for `verified` status only after review by an experienced practitioner and passing its positive, no-op, and contract-risk cases.

## Releases

Releases follow Semantic Versioning:

- Patch: compatible clarification, fixture, harness, or safety correction.
- Minor: backward-compatible capability, profile, case, or optional output addition.
- Major: normative outcome, schema, routing, or behavior change that can alter downstream expectations.

Benchmark results must identify the exact skill version, commit, dataset version, agent configuration, and environment.

## Conflicts of Interest

Reviewers should disclose employment, vendor, benchmark, or product interests that could materially bias a decision. Vendor-specific optimizations must not reduce provider neutrality or be represented as universal evidence.
