# Intent-Driven Naming

An instruction-only Agent Skill that helps AI coding agents choose identifiers by semantic intent instead of programming-language type.

It supports two workflows:

- generating new application code with clear, durable names
- auditing or refactoring dangerous, misleading, ambiguous, or inconsistent identifiers without changing behavior

## Structure

```text
intent-driven-naming/
├── agents/
│   └── openai.yaml
├── references/
│   └── naming-guidelines.md
├── README.md
└── SKILL.md
```

`SKILL.md` stays deliberately small. It defines discovery, routing, workflow, constraints, and completion criteria. The full naming standard lives in `references/naming-guidelines.md` and is loaded only when the skill is selected.

## Install for Codex

Clone the repository into a user-level skill location:

```bash
git clone <repository-url> "$HOME/.agents/skills/intent-driven-naming"
```

For a repository-scoped installation, place it at:

```text
<your-repository>/.agents/skills/intent-driven-naming/
```

## Use

Invoke it explicitly:

```text
$intent-driven-naming Audit the identifiers in this module and rename only dangerous or misleading ones without changing behavior.
```

Or let a compatible agent select it automatically when a coding task matches the description in `SKILL.md`.

## Design Decisions

- Instruction-only: no runtime dependencies or scripts.
- Agent-neutral guidance with optional OpenAI UI metadata.
- Progressive disclosure keeps routine context small.
- Existing behavior and external contracts are protected by default.
- Generic identifiers are evaluated in context rather than mechanically banned.
