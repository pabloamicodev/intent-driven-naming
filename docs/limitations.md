# Limitations

- Semantic naming has multiple valid answers; exact-string goldens are insufficient for most cases.
- Repository vocabulary can be inconsistent or wrong, so local frequency alone is not authority.
- Dynamic languages, reflection, macros, generated code, templates, and external consumers can hide rename surfaces.
- Passing compilation does not prove serialized shapes, public behavior, or operational state stayed compatible.
- Language profiles cannot replace review by experienced practitioners.
- Fixture coverage includes compiled, serialized, dynamic-registry, named-argument, generated-source, query, stateful, security-trust, shell-process, Protobuf-mapping, and telemetry boundaries, but remains representative rather than exhaustive.
- The provider-neutral harness requires an external adapter to run a specific model or coding agent.
- Human calibration and held-out cross-model benchmarks require maintainers and compute outside the offline repository suite. The experiment runner can freeze, execute, resume, and audit that work, but it cannot supply independent experts, private cases, provider access, or representative production populations.
- Context word counts are a stable, reproducible route measure, not exact tokenizer measurements. Release evidence records provider input tokens separately and does not infer universal token savings from word counts.
- The deterministic rename-plan validator checks contract shape and cross-field safety; it cannot prove repository-specific semantics or replace compilation, tests, structural analysis, and review.
- The repository does not claim organization-grade effectiveness until the preregistered held-out control study passes on at least three pinned systems with three complete replicates and two independent human reviews per candidate and pair.

Claims should distinguish structural validity, offline fixture evidence, semantic evaluation, and external organization-grade validation.
