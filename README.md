# Intent-Driven Naming

An instruction-only Agent Skill that helps AI coding agents generate, audit, and safely refactor application-code identifiers according to semantic intent.

The skill combines a reusable naming model with separate workflows for:

- generating new code with clear, durable names;
- auditing dangerous, misleading, ambiguous, or inconsistent identifiers;
- applying behavior-preserving renames without breaking external contracts;
- handling TypeScript, JavaScript, React, and React Query naming patterns.

## Structure

```text
intent-driven-naming/
├── agents/
│   └── openai.yaml
├── evals/
│   ├── behavior-cases.md
│   └── trigger-cases.md
├── references/
│   ├── audit-and-refactor.md
│   ├── naming-model.md
│   ├── new-code-workflow.md
│   ├── refactor-safety.md
│   └── typescript-react-patterns.md
├── README.md
└── SKILL.md
```

`SKILL.md` stays deliberately small. It defines discovery, shared invariants, boundaries, and routing. The agent first loads the semantic model and then only the workflow references relevant to the current task.

This follows the progressive-disclosure model described in [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Install for Codex

Clone or copy the repository into the user-level skills directory so the entrypoint is located at:

```text
$HOME/.agents/skills/intent-driven-naming/SKILL.md
```

For a repository-scoped installation, place it at:

```text
<your-repository>/.agents/skills/intent-driven-naming/
```

## Use

Generate new code:

```text
$intent-driven-naming Implement a checkout service with clear domain names for requests, totals, payment state, and errors.
```

Run a read-only audit:

```text
$intent-driven-naming Audit the identifiers in this module. Rank material problems, but do not edit files.
```

Apply a safe refactor:

```text
$intent-driven-naming Rename dangerous or misleading identifiers in this package without changing behavior or external contracts.
```

Or let a compatible agent select it automatically when a coding task matches the description in `SKILL.md`.

## How Decisions Are Made

The skill starts with the domain concept and adds only distinctions that matter:

```text
concept + role + state + representation + cardinality + unit + necessary scope
```

This is a decision model, not a required naming formula. A candidate is evaluated for truthfulness, disambiguation, consistency, scope fit, searchability, brevity, and contract safety. Existing clear names are preserved.

Audits classify findings as dangerous, misleading, ambiguous, inconsistent, or cosmetic. They also record confidence and contract risk so a suspicious name is not automatically converted into a large refactor.

## Evaluation

The repository includes two evaluation suites:

- `evals/trigger-cases.md` tests whether implicit activation occurs for coding and naming requests but not for branding, prose, file, or branch naming.
- `evals/behavior-cases.md` tests semantic accuracy, no-op decisions, contract preservation, refactor safety, and proportionality.

Run behavior cases both with and without the skill. Score the observable invariants instead of comparing exact response wording. Treat behavior or contract regressions as more severe than missed cosmetic improvements.

When the `description` changes, rerun the trigger cases. When workflows or references change, rerun the affected behavior cases.

## Design Decisions

- Instruction-only: no runtime dependencies or scripts.
- Agent-neutral core guidance with optional OpenAI UI metadata.
- Progressive disclosure keeps unrelated framework and refactor instructions out of context.
- Existing behavior, authorization boundaries, generated sources, and external contracts are protected by default.
- Generic and short identifiers are evaluated in their real scope rather than mechanically banned.
- Audits can produce a justified no-op.
- Language and framework conventions override blanket verbosity.
- Scripts are intentionally omitted because semantic quality cannot be validated reliably by a forbidden-word scan.
