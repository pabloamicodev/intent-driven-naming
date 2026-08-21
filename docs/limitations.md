# Limitations

- Semantic naming has multiple valid answers; exact-string goldens are insufficient for most cases.
- Repository vocabulary can be inconsistent or wrong, so local frequency alone is not authority.
- Dynamic languages, reflection, macros, generated code, templates, and external consumers can hide rename surfaces.
- Passing compilation does not prove serialized shapes, public behavior, or operational state stayed compatible.
- Language profiles cannot replace review by experienced practitioners.
- Fixture coverage now includes compiled, serialized, dynamic-registry, named-argument, generated-source, query, and stateful boundaries, but remains representative rather than exhaustive.
- The provider-neutral harness requires an external adapter to run a specific model or coding agent.
- Human calibration and held-out cross-model benchmarks require maintainers and compute outside the offline repository suite.
- Context word counts are a stable local proxy, not exact tokenizer measurements for every model.
- The repository does not claim organization-grade effectiveness until the three-replicate control study and independent review gates are actually run on pinned external agents.

Claims should distinguish structural validity, offline fixture evidence, semantic evaluation, and external organization-grade validation.
