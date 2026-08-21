# Intent-Driven Naming

An instruction-only Agent Skill that helps AI coding agents generate, audit, and safely refactor software identifiers according to semantic intent in any language or development stack.

The skill combines a reusable naming model with separate workflows for:

- generating new code, queries, schemas, scripts, and infrastructure with clear, durable names;
- auditing dangerous, misleading, ambiguous, or inconsistent identifiers;
- applying behavior-preserving renames without breaking external contracts;
- translating one semantic model into the idioms of each language, framework, schema, and tool.

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
│   ├── data-infrastructure.md
│   ├── dynamic-languages.md
│   ├── functional-concurrent-languages.md
│   ├── language-conventions.md
│   ├── managed-mobile-languages.md
│   ├── naming-model.md
│   ├── new-code-workflow.md
│   ├── refactor-safety.md
│   ├── systems-languages.md
│   └── typescript-javascript.md
├── README.md
└── SKILL.md
```

`SKILL.md` stays deliberately small. It defines discovery, shared invariants, boundaries, and routing. The agent loads the universal semantic model and convention-discovery protocol, then only the workflow and language profile relevant to the current task.

This follows the progressive-disclosure model described in [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Install for Codex

Clone or copy the repository into the user-level skills directory so the entrypoint is located at:

```text
$HOME/.agents/skills/intent-driven-naming/SKILL.md
```

For a repository-scoped installation, place it at:

```text
$REPOSITORY_ROOT/.agents/skills/intent-driven-naming/
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

## Language and Development Coverage

The core is language-independent. Profiles add decisions that genuinely differ by ecosystem:

| Profile | Examples covered |
|---|---|
| TypeScript and JavaScript | Node.js, browser code, React, Vue, Svelte, Angular, React Query |
| Dynamic languages | Python, Ruby, PHP |
| Systems languages | Go, Rust, C, C++ |
| Managed and mobile | Java, Kotlin, C#, Swift, Dart |
| Functional and concurrent | Haskell, OCaml, F#, Scala, Clojure, Erlang, Elixir |
| Data and infrastructure | SQL, data pipelines, schemas, shell, PowerShell, Terraform, Kubernetes, configuration |

These profiles are not an allowlist. For another language, the agent uses `language-conventions.md` to inspect repository instructions, formatters, linters, analyzers, neighboring code, framework requirements, and public contracts before rendering the semantic name.

## How Decisions Are Made

The skill starts with the domain concept and adds only distinctions that matter:

```text
concept + role + state + representation + cardinality + unit + necessary scope
```

This is a decision model, not a required naming formula. A candidate is evaluated for truthfulness, disambiguation, consistency, scope fit, searchability, brevity, idiomatic form, and contract safety. Existing clear names are preserved.

Meaning and spelling are deliberately separated. The same concept may be `priceInCents`, `price_in_cents`, `PriceInCents`, or `PRICE_IN_CENTS` depending on the language and role. Cross-layer consistency means preserving the concept and explicit mappings, not forcing identical casing.

Audits classify findings as dangerous, misleading, ambiguous, inconsistent, or cosmetic. They also record confidence and contract risk so a suspicious name is not automatically converted into a large refactor.

## Evaluation

The repository includes two evaluation suites:

- `evals/trigger-cases.md` contains 30 cases covering application code, systems code, schemas, data, shell, infrastructure, and negative routing boundaries.
- `evals/behavior-cases.md` contains 24 cases testing semantic accuracy, idiomatic rendering, no-op decisions, polyglot continuity, contract preservation, refactor safety, and proportionality.

Run behavior cases both with and without the skill. Score the observable invariants instead of comparing exact response wording. Treat behavior or contract regressions as more severe than missed cosmetic improvements.

When the `description` changes, rerun the trigger cases. When workflows or references change, rerun the affected behavior cases.

## Design Decisions

- Instruction-only: no runtime dependencies or scripts.
- Agent-neutral core guidance with optional OpenAI UI metadata.
- Progressive disclosure keeps unrelated language, framework, and refactor instructions out of context.
- Existing behavior, authorization boundaries, generated sources, and external contracts are protected by default.
- Generic and short identifiers are evaluated in their real scope rather than mechanically banned.
- Audits can produce a justified no-op.
- Language and framework conventions override blanket verbosity.
- Language profiles are optional refinements rather than a closed support list.
- Polyglot consistency preserves meaning while allowing idiomatic casing and API form per layer.
- Scripts are intentionally omitted because semantic quality cannot be validated reliably by a forbidden-word scan.
