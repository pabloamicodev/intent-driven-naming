# Naming Audit and Refactor Decisions

Use this reference to identify naming problems, prioritize them, and decide whether a rename is justified. An audit is evidence gathering; it is not permission to edit code.

## Determine the Requested Outcome

- **Audit or review:** Report findings only. Do not modify files, rename symbols, or expand into architectural cleanup.
- **Targeted refactor:** Apply supported renames within the requested files or symbols.
- **Broad naming cleanup:** Define the affected vocabulary and contract surface before changing cross-module names.

If the request is read-only, remain read-only even when a fix appears obvious.

## Establish Semantic Truth

Do not judge an identifier from its spelling alone. Determine what it represents from:

- declaration and type;
- assignments and transformations;
- callers and consumers;
- return values and control flow;
- tests and fixtures;
- public contracts and serialized forms;
- nearby domain vocabulary.

A generic word is a finding only when it hides useful meaning in its actual scope.

## Classification Rubric

Classify findings by their highest applicable impact.

| Category | Definition | Typical evidence | Default action |
|---|---|---|---|
| Dangerous | The name can cause a wrong assumption, defect, or data corruption. | Missing unit, ID presented as entity, inverted boolean, stale state label. | Fix when authorized and contract-safe. |
| Misleading | The name asserts meaning that the value or behavior does not have. | `activeUsers` includes inactive users; `getOrder` creates one. | Fix when authorized. |
| Ambiguous | The name omits a distinction needed in its scope. | Competing `data`, `result`, or `token` values; unclear representation. | Fix when a clearer meaning is supported. |
| Inconsistent | The name breaks established terminology or a semantic family. | `client` used for the same concept otherwise called `customer`. | Fix when the concepts are truly identical. |
| Cosmetic | The name is understandable and safe but could be marginally cleaner. | Minor wording or preferred style with no semantic gain. | Preserve unless explicitly requested. |

Prioritize dangerous, misleading, and materially ambiguous names. Do not create a large diff for cosmetic consistency.

## Confidence

Assign confidence from evidence, not intuition:

- **High:** Types, behavior, and repository vocabulary agree on one meaning.
- **Medium:** The likely meaning is supported, but one relevant source is incomplete or inconsistent.
- **Low:** Multiple domain interpretations remain plausible or dynamic behavior cannot be traced.

Apply high-confidence renames when authorized. For medium-confidence changes, use the smallest local improvement and state the assumption when it matters. Report low-confidence findings without guessing when a wrong rename could change meaning or public expectations.

## Contract Risk

Classify the rename surface:

- **Internal:** Private local, parameter, callback, or unexported symbol with traceable references.
- **Cross-module:** Exported or shared within the repository.
- **External:** Public API or parameter label, schema, serialized field, environment variable, CLI surface, URL, infrastructure resource address, framework hook, generated interface, or third-party contract.
- **Dynamic:** Referenced by strings, reflection, templates, dependency injection, configuration, or runtime registration.

Internal symbols are normally the safest. Cross-module changes require repository-wide reference analysis. External and dynamic names should be preserved or explicitly mapped at a boundary unless the user authorizes a contract migration.

## Evaluate a Rename Candidate

For each candidate:

1. Write the value's meaning in plain language.
2. Identify the misleading or missing distinction in the current name.
3. Generate one or two candidates using canonical vocabulary.
4. Remove redundant type and scope words.
5. Check related pairs, callers, collections, tests, and public surfaces.
6. Compare semantic gain with diff size and contract risk.
7. Preserve the current name if the gain is marginal.

Example:

```ts
const data = await fetchOrders();
const filtered = data.filter((item) => item.status === "pending");
const result = filtered.reduce((acc, item) => acc + item.total, 0);
```

High-confidence internal improvements:

```ts
const orders = await fetchOrders();
const pendingOrders = orders.filter((order) => order.status === "pending");
const pendingOrdersTotal = pendingOrders.reduce(
  (total, order) => total + order.total,
  0,
);
```

## Audit Output

Lead with the highest-impact findings. Use a compact table when there are several:

| Location | Current name | Category | Evidence | Proposed name | Confidence | Contract risk |
|---|---|---|---|---|---|---|
| `checkout.ts:18` | `price` | Dangerous | Value is stored and charged in cents. | `priceInCents` | High | Internal |

After the findings:

- identify protected identifiers that look unusual but should not change;
- note inconsistent domain vocabulary that needs a human decision;
- state whether the audit found no material issues;
- distinguish required fixes from optional cosmetic suggestions.

Do not manufacture a finding to fill every category.

## Refactor Selection

When edits are authorized, build the smallest rename set that restores semantic integrity:

```text
current symbol -> proposed symbol -> related symbols -> protected boundaries
```

Include related pairs and families only when leaving them unchanged would create a mismatch. A local variable rename does not authorize renaming a public type, parameter label, endpoint, database column, CLI flag, infrastructure resource address, or event name.

Read `refactor-safety.md` before applying changes.

## No-Op Is a Valid Outcome

Preserve identifiers when:

- their meaning is clear within a small scope;
- the proposed alternative is merely longer;
- a generic name is conventional and unambiguous in the framework or language;
- evidence does not support one canonical domain term;
- the semantic improvement is outweighed by contract risk;
- the code is generated and the generator is outside scope.

A trustworthy audit is selective.
