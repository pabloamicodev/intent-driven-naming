# Intent-Driven Naming 1.0.0 Offline Evidence

This artifact records the repository-owned checks run on 2026-08-21 for the version `1.0.0` release candidate. A final release tag must bind the exact commit only after the remaining external gates pass.

## Verified Locally

- The official Skill package validator accepted the package.
- Repository structure, metadata, links, routes, context budgets, generated datasets, schemas, and governance checks passed.
- All 16 unit tests passed.
- Six reference fixtures passed: JavaScript, Python, Rust, Java, SQL, and Terraform.
- The Go fixture was skipped because Go was unavailable in the local environment.
- No critical fixture failed.

The strict CI job installs Go and requires every tool-backed fixture to run. Its result is not claimed here because GitHub Actions has not executed against this local release.

## Conformance Claim

This evidence proves Level 0 package validity. It also supports specific Level 1 routing-budget and Level 3 fixture-safety requirements, but it does not claim either entire level.

It does not prove activation quality, semantic-quality superiority, human-grader agreement, cross-model portability, or organization-grade Level 4 conformance. Those claims require external candidate runs, complete strict scoring, held-out data, pinned configurations, and expert review.

## Reproduction

```text
python scripts/run_checks.py
python harness/verify_fixtures.py --strict-tools
python "$SKILL_CREATOR_ROOT/scripts/quick_validate.py" .
```

Set `SKILL_CREATOR_ROOT` to the host installation of the `skill-creator` skill. Use its bundled `quick_validate.py`.
