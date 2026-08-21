# Behavior Evaluation Cases

Use these cases to test the decisions produced after the skill is selected. Evaluate observable invariants rather than exact wording.

For comparison, run each case once without the skill and once with `$intent-driven-naming`. Record which invariants pass, which fail, and whether the skill introduces unnecessary renames or explanation.

## B01 — New Code Preserves Semantic Stages

### Prompt

```text
Write a TypeScript function that loads users for an organization, keeps active users, and returns their IDs.
```

### Required invariants

- The organization identifier is distinguishable from an organization entity.
- The loaded collection, filtered collection, and returned ID collection have distinguishable names when stored separately.
- Callback parameters use the domain entity rather than `item`.
- No redundant words such as `Array`, `Object`, or `processedData` are introduced.
- The answer focuses on the requested code, not a naming report.

### Failure signals

- `data`, `result`, and `item` carry the main semantic stages.
- A name becomes long by repeating the containing function's entire purpose.

## B02 — Dangerous Unit Ambiguity

### Prompt

```text
Audit and fix this function without changing behavior:

function charge(price: number) {
  return paymentGateway.charge(price);
}

The gateway expects price to be an integer number of cents.
```

### Required invariants

- `price` is classified as dangerous or equivalently high-impact because the unit can be misread.
- The proposed internal name includes cents, such as `priceInCents`.
- The numeric value and gateway call behavior remain unchanged.
- The skill does not introduce currency conversion that was not requested.

## B03 — External Field Is Preserved at the Boundary

### Prompt

```text
Refactor this code for clearer naming without changing the API contract:

const user = apiResponse.usr_id;
return { usr_id: user };
```

### Required invariants

- The external `usr_id` spelling remains unchanged in reads and serialized output.
- The internal value is identified as an ID, for example `userId`.
- The refactor does not replace `usr_id` with `userId` on the wire.

## B04 — Clear Code Produces a No-Op

### Prompt

```text
Audit these identifiers and change only material problems:

const customerOrders = await fetchCustomerOrders(customerId);
const pendingOrders = customerOrders.filter(
  (order) => order.status === "pending",
);
```

### Required invariants

- The skill reports no material naming problem or leaves the code unchanged.
- It does not lengthen `customerOrders`, `pendingOrders`, `order`, or `customerId`.
- Any suggestion is clearly optional rather than presented as a required fix.

## B05 — Conventional Short Local Is Preserved

### Prompt

```text
Improve naming only where it materially helps:

for (let i = 0; i < products.length; i += 1) {
  render(products[i]);
}
```

### Required invariants

- `i` may remain unchanged because it is a conventional index in a tiny scope.
- The skill does not replace it with an excessively descriptive identifier.
- Behavior and loop structure remain unchanged.

## B06 — Domain Vocabulary Remains Continuous

### Prompt

```text
The repository consistently calls a paying organization a customer. Refactor this code:

const client = await customerRepository.findById(accountId);
const clientOrders = await fetchCustomerOrders(client.id);
```

### Required invariants

- The entity becomes `customer` when types and behavior confirm that meaning.
- The identifier becomes `customerId` if it identifies the same customer concept.
- Related names use the `customer` family rather than introducing another synonym.
- The repository name `customerRepository` and function `fetchCustomerOrders` are not renamed without evidence.

## B07 — React Query Families Stay Distinguishable

### Prompt

```text
Refactor this React component so two query results remain clear:

const { data, error, isLoading } = useQuery(customerOrdersOptions);
const { data: data2, error: error2, isLoading: loading2 } = useQuery(productsOptions);
```

### Required invariants

- The two query families are distinguishable by domain.
- The solution may use semantic aliases or grouped query objects.
- Loading booleans read naturally and remain associated with the correct query.
- The library's external property names are not changed.

## B08 — Audit-Only Requests Remain Read-Only

### Prompt

```text
Audit naming in checkout.ts. Rank dangerous and misleading identifiers, but do not edit any files.
```

### Required invariants

- No files are modified.
- Findings include evidence, impact category, proposed name, confidence, and contract risk.
- High-impact findings appear before cosmetic suggestions.
- A lack of material findings is reported honestly.

## B09 — Dynamic Contract Blocks an Unsafe Rename

### Prompt

```text
Rename `paymentHandler` to `authorizePayment` everywhere. Handlers are also loaded from configuration by string name, but the configuration files are not available.
```

### Required invariants

- The missing dynamic configuration is recognized as a contract risk.
- The skill does not claim a safe completed rename without tracing or migrating the string references.
- It either preserves the symbol or reports the precise blocker and required evidence.
- It does not broaden the task into an unrelated handler-registry redesign.

## B10 — Generated Code Is Not Patched Directly

### Prompt

```text
Improve the names in generated/api-client.ts. The file header says it is regenerated from schema/openapi.yaml.
```

### Required invariants

- The generated file is not treated as the durable source of truth.
- The skill looks for an appropriate schema, generator mapping, or generation configuration within scope.
- If the source cannot be changed safely, it reports that limitation instead of making an ephemeral edit.

## B11 — Public API Risk Is Distinguished From Internal Clarity

### Prompt

```text
Our published package exports `getClient(id)`. Internally the domain now uses `customer`. Clean up the naming without breaking consumers.
```

### Required invariants

- The existing public export is preserved unless a compatibility or deprecation path is explicitly authorized.
- Internal code may use `customer` and `customerId` through an adapter or alias.
- The skill does not assume repository search proves there are no external consumers.

## B12 — Boolean Lifecycle Meanings Are Not Collapsed

### Prompt

```text
Name these three React booleans: a request is currently running; the first request has completed at least once; the form is allowed to submit.
```

### Required invariants

- The names distinguish current activity, completed history, and capability.
- Reasonable candidates include patterns such as `isLoading`, `hasLoaded`, and `canSubmit` with domain context where needed.
- The three meanings are not collapsed into variants of `loading`.

## B13 — Language Convention Overrides Blanket Verbosity

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

- The skill recognizes the tiny scope and language convention.
- It does not mechanically replace every short identifier with a long phrase.
- A no-op is acceptable.

## B14 — Audit Categories Stay Evidence-Based

### Prompt

```text
Audit these names: `config`, `result`, `data`, and `item`. You do not have their declarations or usages.
```

### Required invariants

- The words are not automatically declared invalid.
- The skill requests or identifies the missing semantic context needed to classify them.
- It does not invent domain-specific replacements without evidence.

## B15 — Python Preserves External Field Aliases

### Prompt

```text
Refactor this Python API model to use idiomatic internal names while preserving the external JSON field `customerId`.
```

### Required invariants

- Internal Python identifiers use the repository's Python convention, such as `customer_id`.
- The serialized `customerId` field remains unchanged through an alias or adapter.
- The skill does not import JavaScript casing into all Python locals.
- Framework model fields and validation behavior remain intact.

## B16 — Rust Conversion Names Preserve Semantics

### Prompt

```text
Review Rust methods named `to_order`, `into_order`, and `as_order`. Rename only if their ownership behavior and names disagree.
```

### Required invariants

- The audit inspects whether each method borrows, allocates or clones, or consumes its receiver.
- `as_`, `to_`, and `into_` are not treated as interchangeable stylistic prefixes.
- No rename is proposed without evidence from signatures and implementations.
- Public trait and serialization contracts are considered.

## B17 — Java Overrides Remain Stable

### Prompt

```text
Improve method names in this Java class, but several methods implement a third-party interface.
```

### Required invariants

- Interface implementations and overrides retain required signatures.
- Internal helper methods can improve when their meaning is supported.
- The skill does not add vague `Manager`, `Helper`, or `Util` suffixes.
- Reflection, annotations, serializers, and framework lifecycle methods are checked before rename.

## B18 — C# Async Convention Is Contextual

### Prompt

```text
Audit a published C# API containing `FetchOrdersAsync` and an internal local function that also returns a Task.
```

### Required invariants

- The public `Async` suffix is evaluated against .NET and repository API conventions.
- The suffix is not removed merely because the return type already communicates `Task`.
- The internal function is not forced to adopt the same public naming rule without local evidence.
- Public parameter names and named-call compatibility are considered.

## B19 — Swift Argument Labels Are Part of the API

### Prompt

```text
Improve this Swift API: `func orders(_ id: CustomerID)`. Existing callers are outside the repository.
```

### Required invariants

- The full call-site meaning, including argument labels, is evaluated.
- The skill recognizes that changing a public argument label can break source compatibility.
- A clearer new API can be proposed without claiming an uncoordinated rename is behavior-preserving.
- Protocol requirements, Codable keys, and Objective-C selectors are protected when applicable.

## B20 — Functional Pipeline Does Not Gain Object-Oriented Noise

### Prompt

```text
Improve naming in an Elixir pipeline that filters pending orders, groups them by customer ID, and emits `{:orders_ready, payload}` messages.
```

### Required invariants

- Pipeline stages use domain transformations only where intermediate names help.
- Predicates use the language's idiomatic form.
- The message tag `:orders_ready` is treated as a runtime protocol and preserved unless migration is authorized.
- The solution does not introduce managers, setters, or handler classes.

## B21 — SQL Uses Aliases Instead of an Unrequested Migration

### Prompt

```text
The legacy database column `price` stores cents and cannot be migrated. Make this reporting query clearer.
```

### Required invariants

- The stored column remains `price`.
- A semantic query alias such as `price_in_cents` is used when supported by the query context.
- The skill does not convert the value or change its unit.
- Downstream result-shape compatibility is considered before changing a public alias.

## B22 — Terraform Resource Address Is Stateful

### Prompt

```text
Rename `aws_s3_bucket.data` to `customer_exports` in an existing Terraform deployment.
```

### Required invariants

- The resource label is recognized as part of the Terraform state address.
- The skill does not treat the change as a harmless local-variable rename.
- A state move or equivalent migration and plan verification are identified as necessary when authorized.
- The remote resource name, module outputs, and consumers are distinguished from the local label.

## B23 — PowerShell Public Parameters Remain Compatible

### Prompt

```text
Improve a PowerShell function named `Run-CustomerSync` and rename its public `-Id` parameter to something clearer without breaking scripts.
```

### Required invariants

- The command name is evaluated against the module's Verb-Noun convention.
- The public parameter is recognized as a caller-facing interface.
- A compatibility alias or migration is considered instead of a silent breaking rename.
- Automatic and preference variables are not treated as ordinary locals.

## B24 — Polyglot Layers Share Meaning, Not Casing

### Prompt

```text
An API uses `customer_id`, TypeScript uses `customerId`, Python uses `customer_id`, and C# exposes `CustomerId`. Audit their consistency.
```

### Required invariants

- The different casing forms are not reported as inconsistent by themselves.
- The audit verifies that all forms represent the same customer identifier concept.
- Boundary mappings and serialized spellings remain explicit.
- The skill does not force one language's casing across every layer.

## B25 — Callable Name Matches the Observable Contract

### Prompt

```text
Audit a function named `getCustomer` that creates a customer when none exists, persists it, and returns it. Also review its parameters and locals.
```

### Required invariants

- The audit identifies that `getCustomer` hides an observable creation and persistence effect.
- A proposed declaration name reflects the actual contract instead of an incidental implementation step.
- Parameter and local recommendations use the same customer vocabulary as the callable.
- The skill does not claim a public function can be renamed safely without inspecting callers and contracts.

## B26 — Local Names Reveal Meaningful Data-Flow Stages

### Prompt

```text
Improve the names in a function that reads `data`, parses it into `temp`, validates it into `processed`, and returns `result` as a normalized checkout request.
```

### Required invariants

- Names distinguish source, parsed, validated, and normalized representations only where those values coexist or affect correctness.
- Chronological placeholders are replaced by stable semantic states supported by the transformations.
- The function declaration and returned value agree about the final result.
- The skill does not introduce a binding for every trivial expression merely to make the names longer.

## B27 — Short Locals Use a Scope-and-Risk Budget

### Prompt

```text
Review `i`, `x`, `err`, and `acc` in a three-line loop, a one-expression mathematical map, a small Go error branch, and a multi-stage reducer with two monetary accumulators.
```

### Required invariants

- Tiny conventional `i`, `x`, and `err` bindings can remain when unambiguous and idiomatic.
- The reducer's accumulators are evaluated more strictly because multiple monetary meanings coexist.
- Units are added when confusing cents, dollars, tax, or subtotal could cause a wrong assumption.
- The skill does not enforce a minimum identifier length or ban single-letter names.

## B28 — Public Parameter and Private Local Have Different Risk

### Prompt

```text
Refactor a published Python function whose parameter `id` is used by external keyword callers. Its body also has a local `data` containing pending invoices.
```

### Required invariants

- The public parameter is recognized as a keyword-call contract rather than an ordinary local.
- Compatibility, an alias, or a coordinated migration is required before changing `id`.
- The internal `data` binding can become an idiomatic semantic name when its meaning is proven.
- The skill does not import camelCase into Python or conflate the two rename risks.

## B29 — Local Rename Preserves Property Shorthand Contract

### Prompt

```text
In JavaScript, rename local `customerId` to `selectedCustomerId`, but the function returns `{ customerId }` as a public JSON payload.
```

### Required invariants

- The local binding may be renamed while the emitted `customerId` key remains unchanged.
- Property shorthand is expanded to an explicit mapping when necessary.
- Tests or verification include the serialized output shape, not only type checking.
- A global text replacement is rejected as insufficient.

## B30 — Collection, Callback, and Capture Vocabulary Align

### Prompt

```text
Name a function that schedules reminders for pending orders. It filters `items`, maps each `x`, and captures `data` in an async callback used later.
```

### Required invariants

- The callable name describes scheduling order reminders rather than generic processing.
- The collection is plural and callback elements use the aligned singular domain term.
- The captured value receives enough context to remain clear at its later execution site.
- Async or closure boundaries increase the required clarity without forcing verbose names everywhere.

## B31 — Accumulator Names Describe Their Invariants

### Prompt

```text
Improve a reducer with `acc1` for subtotal cents, `acc2` for tax cents, and `n` for the number of billable order lines.
```

### Required invariants

- Each accumulator is named for the value it maintains, not its position in the reducer.
- Monetary units remain explicit because confusing them would be dangerous.
- The counter distinguishes billable line count from monetary totals.
- The surrounding function name and final result use the same order-total vocabulary.

## B32 — Handler and Query Verbs Do Not Hide Effects

### Prompt

```text
Review `handleOrders`, which is a reusable business function that fetches orders, and `getPayment`, which authorizes and persists a payment.
```

### Required invariants

- `handle` is not retained merely as a universal business-logic prefix when no event boundary exists.
- The order function's name sets an accurate data-access expectation using repository evidence.
- `getPayment` is identified as misleading because it hides authorization and persistence effects.
- Replacement names describe observable contracts rather than listing every internal statement.

## B33 — Naming Signal Does Not Authorize Extraction

### Prompt

```text
Rename `doEverything`, a function that validates an order, charges a payment, writes the order, and sends a receipt. This is a naming-only refactor.
```

### Required invariants

- The skill recognizes that a precise name is difficult because the function coordinates several effects.
- A workflow-level name can be proposed if supported by the domain.
- The mixed-responsibility signal is reported separately.
- The skill does not extract functions, redesign the signature, or alter control flow under naming-only authorization.

## B34 — Same Function Intent Renders Idiomatically Across Languages

### Prompt

```text
Implement the same operation in TypeScript, Python, and Elixir: filter pending orders and calculate their total in cents. Name the functions, parameters, predicates, intermediate values, and accumulator idiomatically.
```

### Required invariants

- All implementations preserve the same order, pending-state, total, and cents concepts.
- Casing and predicate forms follow each language rather than being copied from TypeScript.
- Parameters, collections, elements, intermediate values, and results form coherent families in each implementation.
- Conventional functional pipelines are not forced to introduce unnecessary intermediate variables or object-oriented wrappers.

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
