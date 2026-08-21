# Evaluation Adapter Protocol

The harness is provider-neutral. It communicates with an adapter through newline-delimited JSON over standard input and output, so model- or agent-specific authentication remains outside this repository.

## Request

Each input line is one JSON object:

```json
{
  "protocol_version": 1,
  "run_id": "run-2026-08-21",
  "system_id": "codex-gpt-5.6-high",
  "replicate_id": "r1",
  "attempt": 1,
  "case": {
    "id": "B04",
    "suite": "behavior",
    "prompt": "Audit these identifiers..."
  },
  "skill_path": "/absolute/path/to/intent-driven-naming",
  "variant": "with-skill"
}
```

`variant` is `with-skill` or `without-skill`. An adapter MUST isolate cases from one another unless a case explicitly declares conversation state.

## Response

The adapter writes one JSON object per request:

```json
{
  "protocol_version": 1,
  "dataset_version": "1.1.0",
  "run_id": "run-2026-08-21",
  "system_id": "codex-gpt-5.6-high",
  "configuration_hash": "64-lowercase-hex-characters",
  "replicate_id": "r1",
  "attempt": 1,
  "case_id": "B04",
  "variant": "with-skill",
  "status": "completed",
  "selected_skill": true,
  "output_text": "No material naming issues found.",
  "artifact_path": null,
  "artifact_bundle": {
    "format": "none",
    "path": null,
    "sha256": null,
    "verifier_report_path": null
  },
  "loaded_resources": ["SKILL.md", "references/naming-model.md"],
  "usage": {
    "input_tokens": null,
    "output_tokens": null,
    "latency_ms": null,
    "cost_usd": null
  },
  "implementation": {
    "adapter": "example-adapter",
    "adapter_version": "1.0.0",
    "agent": "example-agent",
    "agent_version": "2026-08-21",
    "model": "example-model",
    "model_version": "2026-08-01",
    "reasoning": "high"
  },
  "error": null
}
```

`status` is `completed`, `failed`, or `skipped`. The adapter MUST preserve raw output and MUST NOT grade its own answer. `observed_decisions` and `invariant_grades` are reviewer outputs, not self-evaluation fields for the candidate agent.

The harness owns dataset, run, system, replicate, attempt, case, and variant identity; an adapter MUST echo any supplied values unchanged. The runner computes `configuration_hash` from the canonical implementation metadata. Completed activation responses MUST contain a boolean `selected_skill`. Completed behavior responses MUST put the reviewable answer in `output_text`, a sanitized artifact descriptor in `artifact_bundle`, or both. Unknown result fields, identity mismatches, invalid types, out-of-order cases, and oversized output are rejected before results are written.

## Safety and Reproducibility

- Adapters MUST receive credentials through their host environment, never through dataset files.
- Fixtures MUST run in isolated temporary directories.
- Model names, versions, reasoning settings, agent versions, and adapter versions MUST be recorded with each result. The release policy checks the standard `implementation` fields shown above for both variants.
- Every cohort uses a stable `system_id`; stochastic repetitions use distinct `replicate_id` values. Retried cases increment `attempt`, retain earlier raw records, and record the reason for retry.
- Side-effecting external tools MUST be disabled unless the benchmark explicitly requires and authorizes them.
- The without-skill adapter path MUST omit the skill instructions while preserving every other controlled setting.

## Grading Handoff

The adapter produces observations. Separate graders produce invariant labels, pairwise preferences, or human annotations. This prevents a provider integration from silently changing the evaluation rubric.

For invariant review, `harness/prepare_review.py` emits a blinded packet and a separate private key. Reviewers return evidence-backed records conforming to `review-record.schema.json`. `harness/merge_reviews.py` reattaches labels, computes reviewer agreement, and applies the documented conservative consensus policy. `harness/prepare_pairwise_review.py` separately randomizes A/B position for direct preference judgments. Benchmark operators MUST NOT give reviewers either private key or unblinded result metadata before labels are final.
