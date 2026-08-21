# Compatibility

Compatibility claims are evidence-scoped. Structural support means the skill can route an ecosystem; verified support requires passing cases or fixtures and, for semantic quality, expert review.

| Surface | Status in 1.1.0 | Evidence |
|---|---|---|
| Agent Skills package structure | Validated locally | `SKILL.md`, metadata, routed references, repository validator |
| Codex local skill discovery | Installed and smoke-tested | Runtime-only hash-verified install, official package validation, isolated reference-adapter test |
| Other Agent Skills hosts | Structurally portable | Provider-neutral Markdown core; host behavior must be measured |
| JavaScript contract refactor | Fixture verified | Property shorthand and serialized key |
| TypeScript serialization mapping | Fixture verified | Compiled internal aliases with preserved snake-case wire key |
| Python contract refactor | Fixture verified | Public keyword parameter and local binding |
| Python dynamic lookup | Fixture verified | Runtime registry key and renamed handler declaration |
| Go proportional no-op | Fixture verified when Go is available | Exact no-op and compilation test |
| Rust conversion naming | Fixture verified when Rust is available | Consuming conversion and runtime check |
| Java override safety | Fixture verified when Java is available | Interface signature and runtime check |
| C# named-argument safety | Fixture verified when .NET is available | Public parameter spelling, compilation, and runtime check |
| SQL boundary mapping | Fixture verified | Legacy column and semantic result alias |
| Terraform stateful rename | Fixture verified | Explicit state move and stable remote name |
| Generated TypeScript boundary | Fixture verified | Generator-source change, reproducible regeneration, wire-key preservation, and compilation |

Profiles for additional languages are instructionally supported but are not labeled organization-grade until their corpus, fixtures, and expert review satisfy the declared conformance level.

Model and agent names must be pinned in benchmark artifacts. This repository does not claim universal performance across OpenAI, Anthropic, Google, NVIDIA, or other systems without published run evidence for the exact configuration.
