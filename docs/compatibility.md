# Compatibility

Compatibility claims are evidence-scoped. Structural support means the skill can route an ecosystem; verified support requires passing cases or fixtures and, for semantic quality, expert review.

| Surface | Status in 1.0.0 | Evidence |
|---|---|---|
| Agent Skills package structure | Validated locally | `SKILL.md`, metadata, routed references, repository validator |
| Codex local skill discovery | Designed | Standard skill layout and OpenAI metadata |
| Other Agent Skills hosts | Structurally portable | Provider-neutral Markdown core; host behavior must be measured |
| JavaScript contract refactor | Fixture verified | Property shorthand and serialized key |
| Python contract refactor | Fixture verified | Public keyword parameter and local binding |
| Go proportional no-op | Fixture verified when Go is available | Exact no-op and compilation test |
| Rust conversion naming | Fixture verified when Rust is available | Consuming conversion and runtime check |
| Java override safety | Fixture verified when Java is available | Interface signature and runtime check |
| SQL boundary mapping | Fixture verified | Legacy column and semantic result alias |
| Terraform stateful rename | Fixture verified | Explicit state move and stable remote name |

Profiles for additional languages are instructionally supported but are not labeled organization-grade until their corpus, fixtures, and expert review satisfy the declared conformance level.

Model and agent names must be pinned in benchmark artifacts. This repository does not claim universal performance across OpenAI, Anthropic, Google, NVIDIA, or other systems without published run evidence for the exact configuration.
