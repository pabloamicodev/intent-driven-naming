# Local Variable Naming

Use this reference when a task creates, reviews, or renames parameters used only internally, local bindings, pattern variables, callback parameters, closure captures, accumulators, indexes, errors, or intermediate results. Read `callable-naming.md` too when the declaration itself is in scope.

Local names should reveal meaningful data flow without narrating syntax. The necessary detail grows with distance, competition, transformation depth, and correctness risk.

## Sources and Boundary Aliases

Translate fixed external spellings into internal vocabulary at the boundary:

```ts
const customerId = request.params.customer_id;
```

Keep `request`, `row`, `payload`, `response`, `data`, or `result` when that role is the useful distinction and the scope is unambiguous. Replace a generic name only when evidence supports a better domain meaning.

## Intermediate Transformations

Name a value by what it represents now:

```ts
const parsedRequest = parseCheckoutRequest(requestBody);
const validatedRequest = validateCheckoutRequest(parsedRequest);
const pendingOrders = orders.filter((order) => order.status === "pending");
const ordersByCustomerId = groupOrdersByCustomerId(pendingOrders);
```

Avoid `temp`, `newValue`, `updatedData`, `processed`, `finalResult`, or numbered variants when a stable state is known. Use `previous` and `next` when that relationship is itself meaningful, such as reducers or state transitions.

Do not bind every fluent or functional stage. Introduce a name when it clarifies a domain transition, supports reuse, improves diagnostics, or prevents confusion.

## Collections, Elements, and Families

Use plural collections and aligned singular elements:

```ts
pendingOrders.map((order) => calculateOrderTotal(order));
```

Nested callbacks should keep different roles visible. Related values, errors, statuses, and outputs should share one domain vocabulary rather than introducing synonyms.

## Accumulators, Counters, and Indexes

Name an accumulator by its invariant once its scope or risk exceeds a tiny conventional expression:

```text
orderTotalInCents
ordersByCustomerId
processedOrderCount
maximumRetryDelayMs
```

`acc`, `sum`, `count`, `i`, `j`, and `x` are acceptable in small conventional scopes. Expand them when the body grows, several accumulators coexist, the unit matters, or the value escapes the immediate expression.

## Booleans, Errors, and Results

Preserve distinctions among state, history, capability, policy, and requirement:

```text
isPaymentAuthorized
hasRetriedPayment
canSubmitCheckout
shouldPublishConfirmation
```

Name errors and results by the operation when several coexist:

```text
paymentAuthorizationError
shippingQuoteResult
addressValidationErrors
```

Keep conventional `error`, `err`, or `result` in a tiny unambiguous scope.

## Scope-and-Risk Budget

Increase semantic detail according to:

- distance between declaration and last use;
- competing values with the same base concept;
- transformations already applied;
- closure, branch, async, or nested-scope boundaries;
- risk of confusing an ID, unit, state, representation, or ownership role;
- visibility in logs, errors, tests, or debugging output.

Use the shortest idiomatic name that remains clear under that burden. Do not enforce a minimum length or ban single-letter identifiers.

## Shadowing and Captures

Inspect lexical scope before renaming. Avoid accidental shadowing between parameters, locals, receiver fields, imports, pattern bindings, and nested callbacks.

A short name can become misleading when captured and executed later. Preserve capture, ownership, mutability, hygiene, and concurrency semantics; a rename must not become a hidden rewrite.

## Hidden Contract Traps

Before treating a local rename as mechanical, check:

- object or record shorthand where the binding becomes an emitted field;
- destructuring, pattern matching, aliases, and rest bindings;
- closures, nested functions, macros, templates, and reflection;
- string-based property access, registries, dependency injection, and runtime lookup;
- named arguments or public parameter labels;
- logs, snapshots, telemetry, fixtures, and serialized output;
- generated members and language-specific hygiene or ownership behavior.

Renaming this local can change a JSON contract:

```ts
const customerId = customer.id;
return { customerId };
```

Preserve the key explicitly:

```ts
const selectedCustomerId = customer.id;
return { customerId: selectedCustomerId };
```

Use symbol-aware rename support where available, then inspect literal keys and output shapes separately.

## Audit and Completion Check

1. Trace each important binding through assignments, transformations, branches, captures, and return paths.
2. Identify names that became stale after a transformation.
3. Check collections, elements, accumulators, booleans, errors, and intermediate results at their real scope.
4. Keep conventional short locals when the scope removes ambiguity.
5. Propose the smallest coherent rename family.
6. Verify property keys, captures, named-call compatibility, snapshots, and serialized output.
7. Preserve behavior and avoid unrelated extraction, reordering, or formatting churn.
