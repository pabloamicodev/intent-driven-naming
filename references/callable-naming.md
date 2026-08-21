# Callable Naming

Use this reference when a task creates, reviews, or renames a function, method, constructor, command, query, handler, callback API, or public parameter. Load `local-variable-naming.md` separately when bindings inside the body are also central to the task.

## Start From the Observable Contract

Describe the callable in one sentence from evidence in its callers, inputs, outputs, side effects, failures, and tests:

```text
Given a customer identifier, return that customer's pending orders.
Given order lines, calculate the total price in cents.
Persist an authorized payment and publish its confirmation event.
Answer whether the current user can cancel the order.
```

Name the action or question, its domain object or result, and any state, representation, cardinality, or unit needed by callers. Do not encode a loop, SQL query, cache, or parser unless that mechanism is part of the contract.

## Commands and Effects

Use an action that reveals the observable effect:

```text
authorizePayment
saveShippingAddress
publishOrderConfirmation
cancelPendingSubscription
```

Avoid `do`, `run`, `execute`, `perform`, `manage`, or `process` when a more precise domain action is supported. Preserve them when they are established domain vocabulary or identify a genuine business process.

A query-like name must not hide creation, persistence, publication, deletion, or external communication. `getCustomer` must not silently create one.

## Queries and Computations

When the repository has no stronger convention, these verbs can clarify expectations:

- `get`: retrieve an expected value without claiming transport;
- `find`: search for something that may be absent;
- `list`: return a collection;
- `fetch`: perform remote or asynchronous I/O;
- `read`: consume local storage, a file, or a stream;
- `load`: reconstruct or obtain data whose source is locally understood;
- `calculate`: apply a numeric or business computation;
- `derive`: produce a value from rules or existing state;
- `build` or `create`: construct a value without implying persistence;
- `resolve`: choose or derive an answer from candidates or rules.

This is semantic guidance, not a universal verb dictionary. Project and ecosystem conventions take precedence.

## Predicates

Name predicates as questions or propositions in the target language:

```text
canCancelOrder
hasExpired
isEligibleForTrial
checkout_submittable?
```

Distinguish current state, history, capability, requirement, support, and policy rather than collapsing them into `isValid` or `check`.

## Transformations and Conversions

Expose a meaningful source or destination representation when variants coexist:

```text
parseCheckoutRequest
normalizePhoneNumber
mapApiOrderToOrder
encodeSessionToken
```

Respect language contracts for borrowing, cloning, consuming, parsing, casting, fallibility, or allocation. Prefixes such as `as`, `to`, `into`, `try`, `parse`, and `from` are not stylistic synonyms in ecosystems where they encode semantics.

## Handlers, Callbacks, and Orchestrators

Use `handle` when the callable responds to an event, request, command, or failure. Name the stimulus or outcome, such as `handleCheckoutSubmitted`. Use the ecosystem's `on...` form for callback properties or registration points when appropriate.

Do not rename every business operation to `handle...` merely because a controller or UI calls it.

A name that requires `and` or a long list of verbs can reveal mixed responsibilities. Report that signal without extracting functions or redesigning architecture unless authorized. Name a genuine orchestrator by its business workflow or outcome, such as `completeCheckout` or `provisionWorkspace`.

## Parameters and Argument Labels

A parameter must make sense at the call site and remain truthful in the body:

- use the domain value rather than its language type;
- distinguish an entity from its identifier;
- expose dangerous units or representations;
- keep singular values and plural collections aligned;
- name booleans as propositions or policies when positional booleans are idiomatic;
- avoid repeating context supplied by the receiver, type, module, or namespace.

Public parameter names and argument labels can be source-level contracts in Python, Ruby, Kotlin, C#, Swift, Dart, PowerShell, and other ecosystems. Do not treat them as private locals when callers bind by name.

Signature redesign is not implied by a naming request. Suggesting an options object, overload, or new API is separate unless the user authorizes it.

## Audit a Callable as One Unit

1. Inspect callers, signature, implementation, return paths, side effects, failures, and tests.
2. Compare the declaration name with the observable contract.
3. Check whether parameter names truthfully describe caller inputs.
4. Confirm the returned value and effects fulfill the declaration.
5. Rank declaration-level lies and hidden effects above cosmetic local issues.
6. Check overloads, overrides, protocols, reflection, named arguments, and public consumers before renaming.
7. Preserve the current name when an alternative only adds words.

## Completion Check

- Does the declaration state an accurate action, result, question, or effect?
- Are important side effects visible?
- Do parameters distinguish entities, identifiers, units, and representations where needed?
- Do predicate and conversion forms follow the target ecosystem?
- Are public labels, overrides, protocols, and dynamic contracts preserved?
- Did the naming task remain a naming task rather than an architectural rewrite?
