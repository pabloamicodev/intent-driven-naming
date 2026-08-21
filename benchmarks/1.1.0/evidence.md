# Intent-Driven Naming 1.1.0 Offline Evidence

This directory records repository-owned checks run on 2026-08-21 for version `1.1.0`. It is an auditable offline evidence bundle, not a claim that external organization-grade evaluation has already passed.

## Verified Locally

- The official Skill package validator accepted both the repository source and the installed runtime package.
- The runtime-only package was installed at `C:\Users\pol\.codex\skills\intent-driven-naming`, compared against source by SHA-256, and validated after installation.
- Repository structure, metadata, links, progressive-disclosure routes, one- and two-profile context budgets, generated datasets, release policy, and governance checks passed.
- Eleven JSON Schemas passed Draft 2020-12 schema validation, and all 96 versioned evaluation cases conform to their case schema.
- All 23 unit and integration tests passed, including with-skill/without-skill isolation through the reference Codex CLI adapter using a deterministic fake CLI.
- Ten reference fixtures passed: JavaScript, TypeScript, Python, Rust, Java, C#, SQL, Terraform, dynamic registry, and generated source. The Go fixture was skipped because Go was unavailable locally. No critical fixture failed.
- Python syntax/undefined-name lint passed for the complete repository.

The strict CI job installs every required compiled-language tool and does not allow a missing tool to pass. Its result is not claimed here because GitHub Actions has not executed against this local commit.

## Dataset Boundaries

Dataset version `1.1.0` contains 60 activation cases with an exact 30/30 positive-negative balance and 36 behavior cases with 137 explicitly typed invariants. Activation cases cover five locales; behavior prompts cover English, Spanish, and Portuguese. `evals/manifest.json` binds the Markdown sources and JSONL outputs by SHA-256 and records all declared strata.

## Claims Deliberately Not Made

This bundle does not prove that the skill improves a real external model or agent. The release policy still requires, for every pinned system:

- three complete repetitions of both with-skill and without-skill variants;
- independent evidence-backed semantic reviews and agreement thresholds;
- blinded randomized pairwise comparison;
- activation, slice, behavior, decision, safety, and non-regression gates;
- a measurable positive delta rather than an aggregate tie.

Those runs consume external inference and expert-review resources and must not be fabricated or replaced by the reference fixtures. No final `v1.1.0` release tag should be created until the resulting evidence passes `specification/release-policy.json`.

## Reproduction

```text
python scripts/run_checks.py
python harness/verify_fixtures.py
python scripts/validate_schemas.py
python scripts/install_local_skill.py --destination DESTINATION
python scripts/install_local_skill.py --destination DESTINATION --check
python SKILL_CREATOR_ROOT/scripts/quick_validate.py DESTINATION
```

Use `--strict-tools` for fixture evidence in a provisioned environment. Use the exact adapter, repetition, blinded-review, pairwise, and scoring commands documented in `README.md` for external release evidence.
