# Semantic Naming Model

Use this language-independent model to decide what information an identifier must carry. It is a decision framework, not a formula for producing long names or a casing convention.

## Core Principle

An identifier should tell the truth about the concept it represents and preserve the distinctions that matter in its scope.

Start with the domain concept, then add only the semantic dimensions needed to prevent a wrong inference or a collision with another value.

```text
identifier = concept + necessary distinctions
```

The objective is durable meaning, not maximum description. Select the semantic payload here, then translate it into the target language's idiomatic spelling through `language-conventions.md`.

## Discover the Vocabulary First

Use this evidence order before inventing terminology:

1. Terms explicitly supplied by the user or domain documentation.
2. Public domain types, interfaces, entities, and use-case names.
3. Consistent terminology in the surrounding module and adjacent modules.
4. UI copy, API fields, database schemas, events, and tests that reveal business meaning.
5. A new term only when existing vocabulary is absent, contradictory, or demonstrably misleading.

Treat external names as evidence, not automatic internal names. A fixed external field such as `cust_id` may map to the internal concept “customer identifier” without changing the boundary spelling.

Do not alternate among `customer`, `client`, `user`, and `account` unless they represent different concepts.

## Semantic Dimensions

For each important identifier, determine whether these dimensions matter.

### Concept

What domain entity, value, action, or policy does it represent?

```text
customer
order
shipping address
password reset token
```

### Role or Relationship

How does it relate to another concept?

```text
billing contact
orders indexed by customer identifier
parent organization
assigned reviewer
```

### State or Lifecycle

What meaningful state does the value encode?

```text
pending orders
authenticated user
payment is authorized
expired subscriptions
```

Do not add state that is already guaranteed by the type or scope.

### Representation or Transformation

Which representation coexists with this one, or what meaningful transformation produced it?

```text
raw phone number
normalized phone number
validated checkout request
products sorted by price
orders grouped by customer identifier
```

Avoid sequence-only words such as `new`, `updated`, `processed`, and `final` when the resulting state can be named directly.

### Cardinality and Shape

Is the value one entity, a collection, a set of identifiers, or an index?

```text
selected product
selected products
selected product identifiers
products indexed by identifier
```

Collections are normally plural. Callback parameters preserve the singular entity name.

### Unit or Basis

Could another engineer reasonably assume the wrong unit, currency, time basis, or scale?

```text
request timeout in milliseconds
price in cents
maximum upload size in bytes
discount percentage
creation time in UTC
```

Add a unit only when the domain or type does not make it reliably obvious.

### Scope

Does the current scope contain competing values of the same concept?

Use the local equivalent of `users` when only one user collection exists. Distinguish organization users from account users when both coexist. Do not repeat context already supplied by the module, class, namespace, package, receiver, or schema.

## Decision Procedure

For every important identifier:

1. State in plain language what the value or callable actually represents.
2. Identify nearby values that could be confused with it.
3. Start with the canonical domain concept.
4. Add only the dimensions needed to distinguish its meaning.
5. Remove words that merely repeat type, container, or enclosing scope.
6. Check the candidate against its uses, not only its declaration.
7. Prefer the shortest candidate that remains truthful, consistent, and searchable.

Example:

```text
Meaning: IDs of products currently selected for checkout
Competing values: full selected products and all product IDs
Candidate: selectedCheckoutProductIdentifiers
Reduced: selectedProductIds
```

## Separate Semantics From Surface Form

The same semantic payload can be rendered differently without losing continuity:

```text
JavaScript local: priceInCents
Python local:     price_in_cents
C# property:      PriceInCents
SQL column:       price_in_cents
Environment key: PRICE_IN_CENTS
```

Do not demand identical spelling across layers. Demand that each spelling refer to the same concept and that boundary mappings remain explicit.

## Candidate Quality Test

Compare candidate names using these questions:

- **Truthfulness:** Does the name describe the actual value or effect?
- **Disambiguation:** Does it prevent the likely wrong interpretation?
- **Consistency:** Does it use the codebase's canonical vocabulary?
- **Scope fit:** Is it sufficiently specific for this scope without repeating it?
- **Searchability:** Can an engineer search for the domain concept reliably?
- **Brevity:** Can any word be removed without losing important meaning?
- **Idiomatic form:** Does its casing, affix, visibility, and role match the target ecosystem?
- **Contract safety:** Is the identifier free to change, or is it externally constrained?

Do not use a numeric score mechanically. Prefer a clearly superior candidate; preserve the existing name when tradeoffs are marginal.

## Semantic Families

Identifiers representing the same concept should share terminology. Render related concepts as an idiomatic family in the target ecosystem: customer orders, their error state, their loading state, and the operation that retrieves them should not switch arbitrarily to client purchases or generic data.

Keep related state, mutation, message, and result concepts aligned. A language may express these relationships with setters, mutable references, records, reducers, variants, messages, or transformations; do not impose setter pairs where the language does not use them.

## Booleans as Propositions

Boolean or predicate names should read naturally in the target language and distinguish state, capability, policy, and history:

```ts
isAuthenticated
hasActiveSubscription
canEditProfile
shouldRefetchOrders
needsUserConfirmation
supportsRecurringPayments
requiresShippingAddress
didCompleteCheckout
```

Avoid ambiguous bare nouns equivalent to `permission`, `loading`, and `validation` when the language offers a clearer predicate form. Avoid negative names that create double negatives when a positive proposition expresses the same concept clearly. Respect predicate suffixes or question-mark forms where supported.

## Callables as Actions or Questions

Callables that cause or compute something normally use a precise action plus its object, translated into the target convention. Derive that action from the observable contract across callers, inputs, outputs, side effects, and failure paths rather than from one implementation statement:

```text
calculateOrderTotal
fetchCustomerOrders
normalizePhoneNumber
validateShippingAddress
cancelPendingPayment
```

Predicates should read as questions or propositions according to the language convention:

```text
isEligibleForTrial
hasShippingAddress
canCancelOrder
```

When the codebase has no stronger convention, these verbs can clarify data access semantics:

- `fetch`: obtain through remote or asynchronous I/O.
- `read`: obtain from local storage or a stream.
- `find`: search for something that may be absent.
- `get`: retrieve an expected value without implying the transport.
- `list`: return a collection.
- `resolve`: choose or derive a value from multiple inputs or rules.

Existing project and framework conventions take precedence.

Keep the callable declaration and its body at compatible semantic levels. Parameters should describe what callers provide; meaningful local bindings should describe the value's current role or transformation; the returned value and effects should fulfill the declaration name. Use `function-and-local-naming.md` for the detailed function and intrafunction workflow.

## Contextual Exceptions

Generic or short names are acceptable when their meaning is established by a tiny, conventional scope. Examples include `i` as a loop index, `x` in a short mathematical transform, `err` in a small Go error branch, and `self` or `this` where required by the language.

Type or role affixes can be semantic when they distinguish real architectural roles or contracts, such as a DTO, event, options object, error type, protocol implementation, database row, or message type.

Names such as `config`, `options`, `context`, `result`, or `data` are not forbidden. Improve them only when the scope contains a more useful domain distinction.

## Final Semantic Review

Before completing the selected workflow, ask:

1. What domain concept does this identifier represent?
2. Does the name match the value or effect at every important use?
3. Are entity, ID, collection, state, representation, and unit distinctions preserved where needed?
4. Is the terminology consistent with related identifiers?
5. Does the name remain understandable away from its declaration?
6. Is any word redundant in this scope?
7. Would a rename improve meaning enough to justify its risk and diff size?
8. For a callable, do its parameters, local data flow, returned value, and effects support the declaration name?

If the existing name passes these checks, keep it.
