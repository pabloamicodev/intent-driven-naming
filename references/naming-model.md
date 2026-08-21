# Semantic Naming Model

Use this model to decide what information an identifier must carry. It is a decision framework, not a formula for producing long names.

## Core Principle

An identifier should tell the truth about the concept it represents and preserve the distinctions that matter in its scope.

Start with the domain concept, then add only the semantic dimensions needed to prevent a wrong inference or a collision with another value.

```text
identifier = concept + necessary distinctions
```

The objective is durable meaning, not maximum description.

## Discover the Vocabulary First

Use this evidence order before inventing terminology:

1. Terms explicitly supplied by the user or domain documentation.
2. Public domain types, interfaces, entities, and use-case names.
3. Consistent terminology in the surrounding module and adjacent modules.
4. UI copy, API fields, database schemas, events, and tests that reveal business meaning.
5. A new term only when existing vocabulary is absent, contradictory, or demonstrably misleading.

Treat external names as evidence, not automatic internal names. A fixed external field may be translated at a boundary:

```ts
const customerId = apiResponse.cust_id;
```

Do not alternate among `customer`, `client`, `user`, and `account` unless they represent different concepts.

## Semantic Dimensions

For each important identifier, determine whether these dimensions matter.

### Concept

What domain entity, value, action, or policy does it represent?

```text
customer
order
shippingAddress
passwordResetToken
```

### Role or Relationship

How does it relate to another concept?

```text
billingContact
ordersByCustomerId
parentOrganization
assignedReviewer
```

### State or Lifecycle

What meaningful state does the value encode?

```text
pendingOrders
authenticatedUser
isPaymentAuthorized
expiredSubscriptions
```

Do not add state that is already guaranteed by the type or scope.

### Representation or Transformation

Which representation coexists with this one, or what meaningful transformation produced it?

```text
rawPhoneNumber
normalizedPhoneNumber
validatedCheckoutRequest
productsSortedByPrice
ordersGroupedByCustomerId
```

Avoid sequence-only words such as `new`, `updated`, `processed`, and `final` when the resulting state can be named directly.

### Cardinality and Shape

Is the value one entity, a collection, a set of identifiers, or an index?

```text
selectedProduct
selectedProducts
selectedProductIds
productsById
```

Collections are normally plural. Callback parameters preserve the singular entity name.

### Unit or Basis

Could another engineer reasonably assume the wrong unit, currency, time basis, or scale?

```text
requestTimeoutMs
priceInCents
maximumUploadSizeBytes
discountPercent
createdAtUtc
```

Add a unit only when the domain or type does not make it reliably obvious.

### Scope

Does the current scope contain competing values of the same concept?

Use `users` when only one user collection exists. Use `organizationUsers` and `accountUsers` when both coexist. Do not repeat context already supplied by the module, class, namespace, or receiver.

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

## Candidate Quality Test

Compare candidate names using these questions:

- **Truthfulness:** Does the name describe the actual value or effect?
- **Disambiguation:** Does it prevent the likely wrong interpretation?
- **Consistency:** Does it use the codebase's canonical vocabulary?
- **Scope fit:** Is it sufficiently specific for this scope without repeating it?
- **Searchability:** Can an engineer search for the domain concept reliably?
- **Brevity:** Can any word be removed without losing important meaning?
- **Contract safety:** Is the identifier free to change, or is it externally constrained?

Do not use a numeric score mechanically. Prefer a clearly superior candidate; preserve the existing name when tradeoffs are marginal.

## Semantic Families

Identifiers representing the same concept should share terminology:

```ts
customerOrders
customerOrdersError
areCustomerOrdersLoading
fetchCustomerOrders
```

Keep related pairs aligned:

```ts
selectedProduct
setSelectedProduct

isCheckoutOpen
setIsCheckoutOpen
```

Avoid mismatches such as `product` with `setSelected`, or `orders` with `fetchClientPurchases` when all values represent customer orders.

## Booleans as Propositions

Boolean names should make a condition read naturally and distinguish state, capability, policy, and history:

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

Avoid ambiguous nouns such as `permission`, `loading`, and `validation` for booleans. Avoid negative names that create double negatives when a positive proposition expresses the same concept clearly.

## Callables as Actions or Questions

Functions that cause or compute something normally use a precise action plus its object:

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

## Contextual Exceptions

Generic or short names are acceptable when their meaning is established by a tiny, conventional scope:

```ts
for (let i = 0; i < products.length; i += 1) {
  // `i` is a conventional local index.
}

products.map((product) => product.id);
```

Type or role suffixes can be semantic when they distinguish architectural roles or contracts:

```text
UserDto
PaymentEvent
CheckoutOptions
ValidationError
```

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

If the existing name passes these checks, keep it.
