# Function and Local Naming

Use this reference when a task creates, reviews, or renames a function, method, constructor, parameter, local binding, callback variable, closure capture, or intermediate result. Apply it together with the universal naming model and the relevant language conventions.

The function name should summarize the callable's observable contract. Names inside the function should make its data flow and decisions understandable without narrating syntax. Keep both levels aligned: a well-named function with opaque internals is only partially clear, and precise locals cannot rescue a function name that lies about its effect.

## Start From the Callable Contract

Before choosing the declaration name, describe the callable in one sentence using evidence from its callers, inputs, outputs, side effects, and failures:

```text
Given a customer identifier, return that customer's pending orders.
Given order lines, calculate the total price in cents.
Persist an authorized payment and publish its confirmation event.
Answer whether the current user can cancel the order.
```

Extract the dimensions that callers need to know:

- the domain action or question;
- the object or result of that action;
- whether the callable reads, computes, mutates, emits, validates, converts, or coordinates;
- meaningful state, representation, cardinality, or unit;
- the expected absence or failure model when the ecosystem reflects it in naming;
- the abstraction level of the surrounding module or type.

Do not encode every implementation step in the declaration. A function named for its SQL query, loop, cache, or JSON parsing becomes misleading when those details change unless that mechanism is part of the contract.

## Name Functions and Methods by Role

### Commands and Effects

Use an action that reveals the externally observable effect:

```text
authorizePayment
saveShippingAddress
publishOrderConfirmation
cancelPendingSubscription
```

Avoid weak verbs such as `do`, `run`, `execute`, `perform`, `manage`, or `process` when the code supports a more precise domain action. Preserve them when they are established domain vocabulary or the callable genuinely coordinates a named process.

Do not name a mutating command as though it only returns information. A function called `getOrCreateCustomer` must make the creation effect visible; `getCustomer` must not silently create one.

### Queries and Computations

Choose verbs that set accurate expectations for source and result. When the repository has no stronger convention:

- `get` retrieves an expected value without claiming the transport;
- `find` searches for something that may be absent;
- `list` returns a collection;
- `fetch` performs remote or asynchronous I/O;
- `read` consumes local storage, a file, or a stream;
- `load` reconstructs or obtains data whose source is locally understood;
- `calculate` applies a meaningful numeric or business computation;
- `derive` produces a value from rules or existing state;
- `build` or `create` constructs a new value without implying persistence;
- `resolve` selects or derives an answer from multiple candidates or rules.

Treat this vocabulary as a semantic aid, not a universal verb dictionary. Existing language, framework, and repository conventions take precedence.

### Predicates

Name predicates as questions or propositions in the target language:

```text
canCancelOrder
hasExpired
isEligibleForTrial
checkout_submittable?
```

Distinguish current state, history, capability, requirement, support, and policy. Do not collapse them all into a generic `isValid` or `check`.

### Transformations and Conversions

Expose a meaningful source or destination representation when more than one representation coexists:

```text
parseCheckoutRequest
normalizePhoneNumber
mapApiOrderToOrder
encodeSessionToken
```

Respect language-specific conversion contracts such as borrowing, cloning, consuming, parsing, casting, fallibility, or allocation. Do not treat `as`, `to`, `into`, `try`, `parse`, and `from` as stylistic synonyms where they encode semantics.

### Handlers and Callbacks

Use `handle` when the callable actually responds to an event, request, command, or failure. Name the stimulus or outcome:

```text
handleCheckoutSubmitted
handlePaymentFailure
```

Use the ecosystem's `on...` form for callback properties or registration points when appropriate. Do not rename every business operation to `handle...` merely because a UI or controller calls it.

Anonymous callbacks still need meaningful parameters when their bodies are non-trivial. Keep collection and element vocabulary aligned:

```ts
pendingOrders.map((order) => calculateOrderTotal(order))
```

### Orchestration and Mixed Responsibilities

A name that requires `and` or a long sequence of implementation verbs can reveal that a callable has multiple responsibilities. Report that signal, but do not extract functions or redesign architecture unless the task authorizes it.

For a genuine orchestrator, name the business workflow or outcome rather than listing every step:

```text
completeCheckout
reconcileCustomerAccount
provisionWorkspace
```

Keep the name honest about important side effects. Do not hide persistence, publication, deletion, or external communication behind a purely computational name.

## Name Parameters From the Caller and Callee Perspectives

A parameter should make sense at the call site and remain truthful throughout the function body.

- Use the domain entity or value, not its language type: `customer`, not `customerObject`.
- Distinguish an entity from its identifier: `customerId`, not `customer` when the value is only an ID.
- Make units or representations explicit when a wrong assumption is plausible: `timeoutMs`, `priceInCents`, `encodedToken`.
- Use singular names for one callback element and plural names for collections.
- Name boolean parameters as propositions or policies when positional booleans are acceptable in that ecosystem.
- Prefer a cohesive options value over several unclear boolean parameters only when API design is in scope; a naming task alone does not authorize signature redesign.
- Avoid repeating context already supplied by the method receiver, type, module, or namespace.

Public parameter names and argument labels can be source-level contracts in Python, Ruby, Kotlin, C#, Swift, Dart, PowerShell, and other ecosystems. Do not treat them as private locals when callers can bind by name.

## Make Local Names Describe the Data Flow

Inside a function, name meaningful stages by what the value represents now, not by when it was assigned or which syntax produced it.

### Sources and Boundary Aliases

Translate fixed external spellings into internal vocabulary at the boundary:

```ts
const customerId = request.params.customer_id;
```

Keep `request`, `row`, `payload`, or `response` when that role is the useful distinction. Replace `data` only when the scope contains a supported domain meaning that is more useful.

### Intermediate Transformations

Prefer result-state names:

```ts
const parsedRequest = parseCheckoutRequest(requestBody);
const validatedRequest = validateCheckoutRequest(parsedRequest);
const pendingOrders = orders.filter((order) => order.status === "pending");
const ordersByCustomerId = groupOrdersByCustomerId(pendingOrders);
```

Avoid chronological placeholders such as `temp`, `newValue`, `updatedData`, `processed`, `finalResult`, or numbered variants when a stable semantic state is known. Use `previous` and `next` when the relationship itself matters, such as reducers or state transitions.

Do not create names for every fluent or functional pipeline stage. Introduce a binding when it clarifies a domain transition, supports reuse, improves diagnostics, or prevents confusion.

### Accumulators, Counters, and Indexes

Name an accumulator by its invariant or result once its scope is more than a tiny conventional expression:

```text
orderTotalInCents
ordersByCustomerId
processedOrderCount
maximumRetryDelayMs
```

`acc`, `sum`, `count`, `i`, `j`, `x`, and similar names are acceptable in small conventional scopes where no competing meaning exists. Expand them when the body grows, several accumulators coexist, the unit matters, or the variable escapes the immediate expression.

### Booleans, Errors, and Results

Local booleans should preserve the same semantic distinctions as predicates:

```text
isPaymentAuthorized
hasRetriedPayment
canSubmitCheckout
shouldPublishConfirmation
```

Name errors and results by the relevant operation when several coexist:

```text
paymentAuthorizationError
shippingQuoteResult
addressValidationErrors
```

Keep conventional `error`, `err`, `result`, or language-specific result bindings in a tiny, unambiguous scope.

### Shadowing and Captures

Inspect lexical scope before renaming. Avoid accidental shadowing between parameters, locals, receiver fields, pattern bindings, or nested callbacks. A short local can become misleading when captured by a closure or used far from its declaration.

When a closure captures a value, prefer a name that remains understandable at the capture and execution sites. Preserve required capture, ownership, mutability, and concurrency semantics; a rename must not become a hidden rewrite.

## Use a Scope-and-Risk Budget

The amount of detail a local name needs grows with its semantic burden. Consider:

- distance between declaration and last use;
- number of competing values with the same base concept;
- number of transformations the value has passed through;
- whether it crosses a closure, branch, async boundary, or nested scope;
- risk of confusing an ID, unit, state, representation, or ownership role;
- whether the value appears in logs, errors, tests, or debugging output.

Use the shortest idiomatic name that remains clear under that burden. Do not enforce a minimum length, ban single-letter identifiers, or maximize description mechanically.

## Keep Declaration and Body Coherent

Review the callable as one semantic unit:

1. The function name matches the observable result or effect.
2. Parameter names match what callers provide.
3. Local names expose only meaningful data-flow stages.
4. The returned value fulfills the declaration name.
5. Errors and branches use the same domain vocabulary.
6. Nested callbacks preserve collection-to-element relationships.
7. No internal name introduces a synonym for the same concept without reason.

Example:

```ts
function calculatePendingOrderTotalInCents(orders: Order[]): number {
  const pendingOrders = orders.filter((order) => order.status === "pending");

  return pendingOrders.reduce(
    (orderTotalInCents, order) => orderTotalInCents + order.totalInCents,
    0,
  );
}
```

In a repository where the surrounding scope already guarantees pending orders or cents, shorten the function and local names accordingly. Do not repeat context merely because the standalone example includes it.

## Audit Functions From Uses, Not Spelling

For an existing callable:

1. Inspect its callers, signature, implementation, return paths, side effects, and tests.
2. Compare the declaration name with its observable contract.
3. Trace each important parameter and local through assignments and uses.
4. Identify stale names whose values changed meaning after a transformation.
5. Rank function-level lies and correctness risks above local cosmetic improvements.
6. Propose the smallest coherent rename family.
7. Preserve the existing name when a replacement only adds words.

A vague function name can be material even when every local is clear. A generic local is not a finding when its tiny scope makes its meaning obvious.

## Refactor Traps Inside Functions

Before treating a local rename as mechanically safe, check for:

- object or record shorthand where changing the binding changes an emitted field name;
- destructuring, pattern matching, aliases, and rest bindings;
- closures, captures, nested functions, macros, templates, and reflection;
- string-based property access, dependency injection, registries, and runtime lookup;
- named arguments or parameter labels;
- overloads, overrides, traits, protocols, interfaces, and generated members;
- logs, snapshots, fixtures, telemetry, and serialized output that may expose the spelling;
- language-specific shadowing, ownership, mutability, or hygiene behavior.

For example, renaming only this local can change a JSON contract:

```ts
const customerId = customer.id;
return { customerId };
```

If the output key is fixed, preserve it explicitly while renaming the binding:

```ts
const selectedCustomerId = customer.id;
return { customerId: selectedCustomerId };
```

Use symbol-aware rename support where available, then inspect data shapes and literal contracts separately.

## Completion Check

Before completing a function-sensitive task, verify:

- declaration names state accurate actions, results, questions, or effects;
- parameters distinguish entities, identifiers, collections, units, and representations where needed;
- local names reveal meaningful transitions without narrating syntax;
- short conventional locals remain proportionate to their scope;
- accumulators describe their invariant when ambiguity or risk warrants it;
- function, parameter, local, callback, error, and return vocabulary stay coherent;
- refactors preserve property keys, captures, named-call compatibility, and other hidden contracts;
- no architectural change was smuggled into a naming improvement.
