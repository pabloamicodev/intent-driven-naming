# Behavior Evaluation Cases

Use these cases to test the decisions produced after the skill is selected. Evaluate observable invariants rather than exact wording.

For comparison, run each case once without the skill and once with `$intent-driven-naming`. Record which invariants pass, which fail, and whether the skill introduces unnecessary renames or explanation.

## B01 — New Code Preserves Semantic Stages

### Case metadata

- Mode: generation
- Difficulty: standard
- Locale: en
- Languages: typescript
- Contract risk: internal
- Expected decisions: not-applicable

### Prompt

```text
Write a TypeScript function that loads users for an organization, keeps active users, and returns their IDs.
```

### Required invariants

- [major][semantic] The organization identifier is distinguishable from an organization entity.
- [major][semantic] The loaded collection, filtered collection, and returned ID collection have distinguishable names when stored separately.
- [major][semantic] Callback parameters use the domain entity rather than `item`.
- [major][semantic] No redundant words such as `Array`, `Object`, or `processedData` are introduced.
- [major][semantic] The answer focuses on the requested code, not a naming report.

### Failure signals

- `data`, `result`, and `item` carry the main semantic stages.
- A name becomes long by repeating the containing function's entire purpose.

## B02 — Dangerous Unit Ambiguity

### Case metadata

- Mode: refactor
- Difficulty: standard
- Locale: en
- Languages: typescript
- Contract risk: cross-module
- Expected decisions: rename

### Prompt

```text
Audit and fix this function without changing behavior:

function charge(price: number) {
  return paymentGateway.charge(price);
}

The gateway expects price to be an integer number of cents.
```

### Required invariants

- [major][semantic] `price` is classified as dangerous or equivalently high-impact because the unit can be misread.
- [major][semantic] The proposed internal name includes cents, such as `priceInCents`.
- [critical][semantic] The numeric value and gateway call behavior remain unchanged.
- [major][semantic] The skill does not introduce currency conversion that was not requested.

## B03 — External Field Is Preserved at the Boundary

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: javascript
- Contract risk: external
- Expected decisions: map

### Prompt

```text
Refactor this code for clearer naming without changing the API contract:

const user = apiResponse.usr_id;
return { usr_id: user };
```

### Required invariants

- [critical][semantic] The external `usr_id` spelling remains unchanged in reads and serialized output.
- [major][semantic] The internal value is identified as an ID, for example `userId`.
- [critical][semantic] The refactor does not replace `usr_id` with `userId` on the wire.

## B04 — Clear Code Produces a No-Op

### Case metadata

- Mode: audit
- Difficulty: edge
- Locale: en
- Languages: javascript
- Contract risk: internal
- Expected decisions: keep

### Prompt

```text
Audit these identifiers and change only material problems:

const customerOrders = await fetchCustomerOrders(customerId);
const pendingOrders = customerOrders.filter(
  (order) => order.status === "pending",
);
```

### Required invariants

- [critical][semantic] The skill reports no material naming problem or leaves the code unchanged.
- [major][semantic] It does not lengthen `customerOrders`, `pendingOrders`, `order`, or `customerId`.
- [major][semantic] Any suggestion is clearly optional rather than presented as a required fix.

## B05 — Conventional Short Local Is Preserved

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: javascript
- Contract risk: internal
- Expected decisions: keep

### Prompt

```text
Improve naming only where it materially helps:

for (let i = 0; i < products.length; i += 1) {
  render(products[i]);
}
```

### Required invariants

- [critical][semantic] `i` may remain unchanged because it is a conventional index in a tiny scope.
- [critical][semantic] The skill does not replace it with an excessively descriptive identifier.
- [critical][semantic] Behavior and loop structure remain unchanged.

## B06 — Domain Vocabulary Remains Continuous

### Case metadata

- Mode: refactor
- Difficulty: standard
- Locale: en
- Languages: javascript
- Contract risk: internal
- Expected decisions: keep, rename

### Prompt

```text
The repository consistently calls a paying organization a customer. Refactor this code:

const client = await customerRepository.findById(accountId);
const clientOrders = await fetchCustomerOrders(client.id);
```

### Required invariants

- [critical][semantic] The entity becomes `customer` when types and behavior confirm that meaning.
- [major][semantic] The identifier becomes `customerId` if it identifies the same customer concept.
- [major][semantic] Related names use the `customer` family rather than introducing another synonym.
- [major][semantic] The repository name `customerRepository` and function `fetchCustomerOrders` are not renamed without evidence.

## B07 — React Query Families Stay Distinguishable

### Case metadata

- Mode: refactor
- Difficulty: standard
- Locale: en
- Languages: typescript, react
- Contract risk: internal
- Expected decisions: rename

### Prompt

```text
Refactor this React component so two query results remain clear:

const { data, error, isLoading } = useQuery(customerOrdersOptions);
const { data: data2, error: error2, isLoading: loading2 } = useQuery(productsOptions);
```

### Required invariants

- [major][semantic] The two query families are distinguishable by domain.
- [major][semantic] The solution may use semantic aliases or grouped query objects.
- [major][semantic] Loading booleans read naturally and remain associated with the correct query.
- [critical][semantic] The library's external property names are not changed.

## B08 — Audit-Only Requests Remain Read-Only

### Case metadata

- Mode: audit
- Difficulty: edge
- Locale: en
- Languages: typescript
- Contract risk: internal
- Expected decisions: keep

### Prompt

```text
Audit naming in checkout.ts. Rank dangerous and misleading identifiers, but do not edit any files.
```

### Required invariants

- [critical][semantic] No files are modified.
- [critical][semantic] Findings include evidence, impact category, proposed name, confidence, and contract risk.
- [major][semantic] High-impact findings appear before cosmetic suggestions.
- [major][semantic] A lack of material findings is reported honestly.

## B09 — Dynamic Contract Blocks an Unsafe Rename

### Case metadata

- Mode: refactor
- Difficulty: adversarial
- Locale: en
- Languages: generic
- Contract risk: dynamic
- Expected decisions: defer

### Prompt

```text
Rename `paymentHandler` to `authorizePayment` everywhere. Handlers are also loaded from configuration by string name, but the configuration files are not available.
```

### Required invariants

- [critical][semantic] The missing dynamic configuration is recognized as a contract risk.
- [major][semantic] The skill does not claim a safe completed rename without tracing or migrating the string references.
- [major][semantic] It either preserves the symbol or reports the precise blocker and required evidence.
- [major][semantic] It does not broaden the task into an unrelated handler-registry redesign.

## B10 — Generated Code Is Not Patched Directly

### Case metadata

- Mode: refactor
- Difficulty: adversarial
- Locale: en
- Languages: typescript
- Contract risk: external
- Expected decisions: defer

### Prompt

```text
Improve the names in generated/api-client.ts. The file header says it is regenerated from schema/openapi.yaml.
```

### Required invariants

- [major][semantic] The generated file is not treated as the durable source of truth.
- [major][semantic] The skill looks for an appropriate schema, generator mapping, or generation configuration within scope.
- [major][semantic] If the source cannot be changed safely, it reports that limitation instead of making an ephemeral edit.

## B11 — Public API Risk Is Distinguished From Internal Clarity

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: generic
- Contract risk: external
- Expected decisions: map, migrate

### Prompt

```text
Our published package exports `getClient(id)`. Internally the domain now uses `customer`. Clean up the naming without breaking consumers.
```

### Required invariants

- [critical][semantic] The existing public export is preserved unless a compatibility or deprecation path is explicitly authorized.
- [major][semantic] Internal code may use `customer` and `customerId` through an adapter or alias.
- [critical][semantic] The skill does not assume repository search proves there are no external consumers.

## B12 — Boolean Lifecycle Meanings Are Not Collapsed

### Case metadata

- Mode: audit
- Difficulty: edge
- Locale: en
- Languages: typescript, react
- Contract risk: internal
- Expected decisions: keep, rename

### Prompt

```text
Name these three React booleans: a request is currently running; the first request has completed at least once; the form is allowed to submit.
```

### Required invariants

- [major][semantic] The names distinguish current activity, completed history, and capability.
- [major][semantic] Reasonable candidates include patterns such as `isLoading`, `hasLoaded`, and `canSubmit` with domain context where needed.
- [major][semantic] The three meanings are not collapsed into variants of `loading`.

## B13 — Language Convention Overrides Blanket Verbosity

### Case metadata

- Mode: audit
- Difficulty: edge
- Locale: en
- Languages: go
- Contract risk: internal
- Expected decisions: keep

### Prompt

```text
Review this idiomatic Go helper and improve only dangerous or misleading names:

func sum(xs []int) int {
    n := 0
    for _, x := range xs {
        n += x
    }
    return n
}
```

### Required invariants

- [major][semantic] The skill recognizes the tiny scope and language convention.
- [major][semantic] It does not mechanically replace every short identifier with a long phrase.
- [major][semantic] A no-op is acceptable.

## B14 — Audit Categories Stay Evidence-Based

### Case metadata

- Mode: audit
- Difficulty: adversarial
- Locale: en
- Languages: generic
- Contract risk: unknown
- Expected decisions: defer

### Prompt

```text
Audit these names: `config`, `result`, `data`, and `item`. You do not have their declarations or usages.
```

### Required invariants

- [major][semantic] The words are not automatically declared invalid.
- [major][semantic] The skill requests or identifies the missing semantic context needed to classify them.
- [major][semantic] It does not invent domain-specific replacements without evidence.

## B15 — Python Preserves External Field Aliases

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: python
- Contract risk: external
- Expected decisions: map

### Prompt

```text
Refactor this Python API model to use idiomatic internal names while preserving the external JSON field `customerId`.
```

### Required invariants

- [major][semantic] Internal Python identifiers use the repository's Python convention, such as `customer_id`.
- [critical][semantic] The serialized `customerId` field remains unchanged through an alias or adapter.
- [major][semantic] The skill does not import JavaScript casing into all Python locals.
- [critical][semantic] Framework model fields and validation behavior remain intact.

## B16 — Rust Conversion Names Preserve Semantics

### Case metadata

- Mode: audit
- Difficulty: edge
- Locale: en
- Languages: rust
- Contract risk: external
- Expected decisions: keep, rename, defer

### Prompt

```text
Review Rust methods named `to_order`, `into_order`, and `as_order`. Rename only if their ownership behavior and names disagree.
```

### Required invariants

- [major][semantic] The audit inspects whether each method borrows, allocates or clones, or consumes its receiver.
- [major][semantic] `as_`, `to_`, and `into_` are not treated as interchangeable stylistic prefixes.
- [major][semantic] No rename is proposed without evidence from signatures and implementations.
- [critical][semantic] Public trait and serialization contracts are considered.

## B17 — Java Overrides Remain Stable

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: java
- Contract risk: external
- Expected decisions: keep, rename

### Prompt

```text
Improve method names in this Java class, but several methods implement a third-party interface.
```

### Required invariants

- [major][semantic] Interface implementations and overrides retain required signatures.
- [major][semantic] Internal helper methods can improve when their meaning is supported.
- [major][semantic] The skill does not add vague `Manager`, `Helper`, or `Util` suffixes.
- [major][semantic] Reflection, annotations, serializers, and framework lifecycle methods are checked before rename.

## B18 — C# Async Convention Is Contextual

### Case metadata

- Mode: audit
- Difficulty: edge
- Locale: en
- Languages: csharp
- Contract risk: external
- Expected decisions: keep

### Prompt

```text
Audit a published C# API containing `FetchOrdersAsync` and an internal local function that also returns a Task.
```

### Required invariants

- [critical][semantic] The public `Async` suffix is evaluated against .NET and repository API conventions.
- [major][semantic] The suffix is not removed merely because the return type already communicates `Task`.
- [critical][semantic] The internal function is not forced to adopt the same public naming rule without local evidence.
- [critical][semantic] Public parameter names and named-call compatibility are considered.

## B19 — Swift Argument Labels Are Part of the API

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: swift
- Contract risk: external
- Expected decisions: migrate, defer

### Prompt

```text
Improve this Swift API: `func orders(_ id: CustomerID)`. Existing callers are outside the repository.
```

### Required invariants

- [major][semantic] The full call-site meaning, including argument labels, is evaluated.
- [critical][semantic] The skill recognizes that changing a public argument label can break source compatibility.
- [critical][semantic] A clearer new API can be proposed without claiming an uncoordinated rename is behavior-preserving.
- [major][semantic] Protocol requirements, Codable keys, and Objective-C selectors are protected when applicable.

## B20 — Functional Pipeline Does Not Gain Object-Oriented Noise

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: elixir
- Contract risk: dynamic
- Expected decisions: keep, rename

### Prompt

```text
Improve naming in an Elixir pipeline that filters pending orders, groups them by customer ID, and emits `{:orders_ready, payload}` messages.
```

### Required invariants

- [major][semantic] Pipeline stages use domain transformations only where intermediate names help.
- [major][semantic] Predicates use the language's idiomatic form.
- [critical][semantic] The message tag `:orders_ready` is treated as a runtime protocol and preserved unless migration is authorized.
- [major][semantic] The solution does not introduce managers, setters, or handler classes.

## B21 — SQL Uses Aliases Instead of an Unrequested Migration

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: sql
- Contract risk: external
- Expected decisions: map

### Prompt

```text
The legacy database column `price` stores cents and cannot be migrated. Make this reporting query clearer.
```

### Required invariants

- [major][semantic] The stored column remains `price`.
- [major][semantic] A semantic query alias such as `price_in_cents` is used when supported by the query context.
- [major][semantic] The skill does not convert the value or change its unit.
- [critical][semantic] Downstream result-shape compatibility is considered before changing a public alias.

## B22 — Terraform Resource Address Is Stateful

### Case metadata

- Mode: refactor
- Difficulty: adversarial
- Locale: en
- Languages: terraform
- Contract risk: stateful
- Expected decisions: migrate

### Prompt

```text
Rename `aws_s3_bucket.data` to `customer_exports` in an existing Terraform deployment.
```

### Required invariants

- [major][semantic] The resource label is recognized as part of the Terraform state address.
- [major][semantic] The skill does not treat the change as a harmless local-variable rename.
- [major][semantic] A state move or equivalent migration and plan verification are identified as necessary when authorized.
- [major][semantic] The remote resource name, module outputs, and consumers are distinguished from the local label.

## B23 — PowerShell Public Parameters Remain Compatible

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: powershell
- Contract risk: external
- Expected decisions: map, migrate

### Prompt

```text
Improve a PowerShell function named `Run-CustomerSync` and rename its public `-Id` parameter to something clearer without breaking scripts.
```

### Required invariants

- [major][semantic] The command name is evaluated against the module's Verb-Noun convention.
- [critical][semantic] The public parameter is recognized as a caller-facing interface.
- [major][semantic] A compatibility alias or migration is considered instead of a silent breaking rename.
- [major][semantic] Automatic and preference variables are not treated as ordinary locals.

## B24 — Polyglot Layers Share Meaning, Not Casing

### Case metadata

- Mode: audit
- Difficulty: edge
- Locale: en
- Languages: typescript, python, csharp
- Contract risk: external
- Expected decisions: keep, map

### Prompt

```text
An API uses `customer_id`, TypeScript uses `customerId`, Python uses `customer_id`, and C# exposes `CustomerId`. Audit their consistency.
```

### Required invariants

- [major][semantic] The different casing forms are not reported as inconsistent by themselves.
- [major][semantic] The audit verifies that all forms represent the same customer identifier concept.
- [critical][semantic] Boundary mappings and serialized spellings remain explicit.
- [major][semantic] The skill does not force one language's casing across every layer.

## B25 — Callable Name Matches the Observable Contract

### Case metadata

- Mode: audit
- Difficulty: standard
- Locale: en
- Languages: generic
- Contract risk: external
- Expected decisions: rename, defer

### Prompt

```text
Audit a function named `getCustomer` that creates a customer when none exists, persists it, and returns it. Also review its parameters and locals.
```

### Required invariants

- [major][semantic] The audit identifies that `getCustomer` hides an observable creation and persistence effect.
- [critical][semantic] A proposed declaration name reflects the actual contract instead of an incidental implementation step.
- [major][semantic] Parameter and local recommendations use the same customer vocabulary as the callable.
- [critical][semantic] The skill does not claim a public function can be renamed safely without inspecting callers and contracts.

## B26 — Local Names Reveal Meaningful Data-Flow Stages

### Case metadata

- Mode: refactor
- Difficulty: standard
- Locale: en
- Languages: generic
- Contract risk: internal
- Expected decisions: rename

### Prompt

```text
Improve the names in a function that reads `data`, parses it into `temp`, validates it into `processed`, and returns `result` as a normalized checkout request.
```

### Required invariants

- [major][semantic] Names distinguish source, parsed, validated, and normalized representations only where those values coexist or affect correctness.
- [major][semantic] Chronological placeholders are replaced by stable semantic states supported by the transformations.
- [major][semantic] The function declaration and returned value agree about the final result.
- [major][semantic] The skill does not introduce a binding for every trivial expression merely to make the names longer.

## B27 — Short Locals Use a Scope-and-Risk Budget

### Case metadata

- Mode: audit
- Difficulty: edge
- Locale: en
- Languages: go
- Contract risk: internal
- Expected decisions: keep, rename

### Prompt

```text
Review `i`, `x`, `err`, and `acc` in a three-line loop, a one-expression mathematical map, a small Go error branch, and a multi-stage reducer with two monetary accumulators.
```

### Required invariants

- [major][semantic] Tiny conventional `i`, `x`, and `err` bindings can remain when unambiguous and idiomatic.
- [major][semantic] The reducer's accumulators are evaluated more strictly because multiple monetary meanings coexist.
- [major][semantic] Units are added when confusing cents, dollars, tax, or subtotal could cause a wrong assumption.
- [major][semantic] The skill does not enforce a minimum identifier length or ban single-letter names.

## B28 — Public Parameter and Private Local Have Different Risk

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: en
- Languages: python
- Contract risk: external
- Expected decisions: map, rename

### Prompt

```text
Refactor a published Python function whose parameter `id` is used by external keyword callers. Its body also has a local `data` containing pending invoices.
```

### Required invariants

- [critical][semantic] The public parameter is recognized as a keyword-call contract rather than an ordinary local.
- [major][semantic] Compatibility, an alias, or a coordinated migration is required before changing `id`.
- [major][semantic] The internal `data` binding can become an idiomatic semantic name when its meaning is proven.
- [major][semantic] The skill does not import camelCase into Python or conflate the two rename risks.

## B29 — Local Rename Preserves Property Shorthand Contract

### Case metadata

- Mode: refactor
- Difficulty: adversarial
- Locale: en
- Languages: javascript
- Contract risk: external
- Expected decisions: map

### Prompt

```text
In JavaScript, rename local `customerId` to `selectedCustomerId`, but the function returns `{ customerId }` as a public JSON payload.
```

### Required invariants

- [critical][semantic] The local binding may be renamed while the emitted `customerId` key remains unchanged.
- [major][semantic] Property shorthand is expanded to an explicit mapping when necessary.
- [critical][semantic] Tests or verification include the serialized output shape, not only type checking.
- [major][semantic] A global text replacement is rejected as insufficient.

## B30 — Collection, Callback, and Capture Vocabulary Align

### Case metadata

- Mode: generation
- Difficulty: standard
- Locale: en
- Languages: generic
- Contract risk: internal
- Expected decisions: not-applicable

### Prompt

```text
Name a function that schedules reminders for pending orders. It filters `items`, maps each `x`, and captures `data` in an async callback used later.
```

### Required invariants

- [major][semantic] The callable name describes scheduling order reminders rather than generic processing.
- [major][semantic] The collection is plural and callback elements use the aligned singular domain term.
- [major][semantic] The captured value receives enough context to remain clear at its later execution site.
- [major][semantic] Async or closure boundaries increase the required clarity without forcing verbose names everywhere.

## B31 — Accumulator Names Describe Their Invariants

### Case metadata

- Mode: refactor
- Difficulty: standard
- Locale: en
- Languages: generic
- Contract risk: internal
- Expected decisions: rename

### Prompt

```text
Improve a reducer with `acc1` for subtotal cents, `acc2` for tax cents, and `n` for the number of billable order lines.
```

### Required invariants

- [major][semantic] Each accumulator is named for the value it maintains, not its position in the reducer.
- [major][semantic] Monetary units remain explicit because confusing them would be dangerous.
- [major][semantic] The counter distinguishes billable line count from monetary totals.
- [major][semantic] The surrounding function name and final result use the same order-total vocabulary.

## B32 — Handler and Query Verbs Do Not Hide Effects

### Case metadata

- Mode: audit
- Difficulty: standard
- Locale: en
- Languages: generic
- Contract risk: internal
- Expected decisions: rename

### Prompt

```text
Review `handleOrders`, which is a reusable business function that fetches orders, and `getPayment`, which authorizes and persists a payment.
```

### Required invariants

- [major][semantic] `handle` is not retained merely as a universal business-logic prefix when no event boundary exists.
- [major][semantic] The order function's name sets an accurate data-access expectation using repository evidence.
- [major][semantic] `getPayment` is identified as misleading because it hides authorization and persistence effects.
- [critical][semantic] Replacement names describe observable contracts rather than listing every internal statement.

## B33 — Naming Signal Does Not Authorize Extraction

### Case metadata

- Mode: refactor
- Difficulty: adversarial
- Locale: en
- Languages: generic
- Contract risk: internal
- Expected decisions: rename

### Prompt

```text
Rename `doEverything`, a function that validates an order, charges a payment, writes the order, and sends a receipt. This is a naming-only refactor.
```

### Required invariants

- [major][semantic] The skill recognizes that a precise name is difficult because the function coordinates several effects.
- [major][semantic] A workflow-level name can be proposed if supported by the domain.
- [major][semantic] The mixed-responsibility signal is reported separately.
- [major][semantic] The skill does not extract functions, redesign the signature, or alter control flow under naming-only authorization.

## B34 — Same Function Intent Renders Idiomatically Across Languages

### Case metadata

- Mode: generation
- Difficulty: edge
- Locale: en
- Languages: typescript, python, elixir
- Contract risk: internal
- Expected decisions: not-applicable

### Prompt

```text
Implement the same operation in TypeScript, Python, and Elixir: filter pending orders and calculate their total in cents. Name the functions, parameters, predicates, intermediate values, and accumulator idiomatically.
```

### Required invariants

- [major][semantic] All implementations preserve the same order, pending-state, total, and cents concepts.
- [major][semantic] Casing and predicate forms follow each language rather than being copied from TypeScript.
- [major][semantic] Parameters, collections, elements, intermediate values, and results form coherent families in each implementation.
- [major][semantic] Conventional functional pipelines are not forced to introduce unnecessary intermediate variables or object-oriented wrappers.

## B35 — Variables Locales Expresan el Flujo de Datos

### Case metadata

- Mode: refactor
- Difficulty: standard
- Locale: es
- Languages: javascript
- Contract risk: internal
- Expected decisions: rename

### Prompt

```text
Mejora los nombres de la función y de las variables internas sin cambiar su comportamiento:

function calc(data) {
  let r = 0;
  for (const x of data) {
    if (x.status === "paid") r += x.amount_in_cents;
  }
  return r;
}
```

### Required invariants

- [major][semantic] The function name communicates that it totals paid invoice amounts in cents.
- [major][semantic] The collection and element form a coherent plural and singular invoice pair.
- [major][semantic] The accumulator states both its paid-invoice meaning and cents unit at the point where those distinctions matter.
- [critical][semantic] The paid-state filter, `amount_in_cents` contract spelling, iteration, and numeric result remain unchanged.

## B36 — Registro Dinâmico Preserva a Chave de Runtime

### Case metadata

- Mode: refactor
- Difficulty: edge
- Locale: pt
- Languages: python
- Contract risk: dynamic
- Expected decisions: keep, rename

### Prompt

```text
Melhore os nomes internos, mas preserve o comportamento e o contrato de registro dinâmico:

@register("invoice.created")
def do(data):
    return enqueue(data["invoice_id"])
```

### Required invariants

- [critical][semantic] The runtime registration key `invoice.created` remains unchanged.
- [major][semantic] The handler declaration communicates the invoice-created event rather than retaining `do`.
- [major][semantic] The parameter communicates that it is the event payload without inventing a richer domain type.
- [critical][semantic] The `invoice_id` lookup and enqueue behavior remain unchanged.

## Scoring

Score each required invariant as:

- `pass`: observable in the result;
- `fail`: contradicted or omitted when applicable;
- `not-applicable`: the execution environment cannot exercise it.

Track these aggregate dimensions:

- semantic accuracy;
- contract preservation;
- behavior preservation;
- proportionality of rename scope;
- respect for language conventions;
- preservation of language-specific API, protocol, schema, ABI, CLI, and infrastructure contracts;
- semantic continuity across polyglot layers without forced casing uniformity;
- coherence between callable declarations, parameters, locals, errors, returned values, and effects;
- scope-sensitive treatment of conventional short locals, callbacks, captures, and accumulators;
- preservation of property keys, named-argument compatibility, and other intrafunction contract surfaces;
- ability to produce a no-op;
- quality of audit evidence;
- absence of unnecessary explanation in generation mode.

Treat a contract-safety or behavior-preservation failure as more severe than a missed cosmetic improvement.
