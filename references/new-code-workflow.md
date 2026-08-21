# New-Code Naming Workflow

Apply this workflow while designing non-trivial software in any programming language, query language, schema, or infrastructure format. Naming is part of the implementation, not a cleanup phase detached from behavior.

## 1. Establish the Domain Language

Before choosing identifiers:

- identify the entities and use cases named by the request;
- inspect nearby types, functions, modules, tests, and UI language when working in an existing repository;
- distinguish terms that are synonyms from terms that represent separate roles;
- preserve externally fixed vocabulary at boundaries even when internal terminology is clearer.

When the domain is unclear, use the most specific meaning supported by evidence. Do not invent business distinctions merely to create descriptive names.

## 2. Inventory Important Values

Pay particular attention to values whose meaning can change or be confused:

- entities and their identifiers;
- individual values and collections;
- raw, parsed, normalized, validated, and persisted representations;
- booleans and lifecycle states;
- amounts, units, currencies, durations, sizes, and percentages;
- derived and transformed values;
- callbacks, event handlers, and asynchronous results;
- callable declarations, parameters, closure captures, accumulators, and intermediate data-flow stages;
- errors, options, policies, and configuration;
- public functions, exported types, and cross-module concepts.

Tiny conventional locals do not require the same descriptive burden as long-lived or cross-module identifiers.

## 3. Apply the Semantic Model

Use the naming model to build the shortest unambiguous semantic payload, then render it according to the target language and project conventions.

Equivalent intent can have different idiomatic spellings:

```text
TypeScript: const priceInCents = 2_499;
Python:     price_in_cents = 2_499
C#:         public int PriceInCents { get; init; }
SQL:        price_in_cents INTEGER NOT NULL
```

Do not copy casing, visibility, or affixes from an example written in another ecosystem.

Avoid naming by programming-language type:

```ts
const userObject = getUser();
const productArray = getProducts();
const responseData = response.data;
```

Prefer domain meaning and state:

```ts
const user = getUser();
const products = getProducts();
const availableProducts = response.data;
```

Distinguish an entity from its identifier:

```ts
const customerId = request.params.customerId;
const customer = await customerRepository.findById(customerId);
```

Distinguish representations only when they coexist or correctness depends on them:

```ts
const rawPhoneNumber = formData.phone;
const normalizedPhoneNumber = normalizePhoneNumber(rawPhoneNumber);
```

Describe a transformation by its resulting meaning:

```ts
const activeUsers = users.filter((user) => user.isActive);
const ordersByCustomerId = groupOrdersByCustomerId(orders);
const productsSortedByPrice = sortProductsByPrice(products);
```

Include units when ambiguity could produce incorrect behavior:

```ts
const requestTimeoutMs = 5_000;
const cacheDurationSeconds = 60;
const priceInCents = 2_499;
const maximumUploadSizeBytes = 1_024;
```

## 4. Maintain Local Naming Integrity

Check relationships among identifiers, not only individual names.

### Collections and Elements

```ts
const pendingOrders = await fetchPendingOrders();

pendingOrders.forEach((order) => {
  sendOrderReminder(order);
});
```

### Maps, Sets, and Identifier Collections

Name the indexing or membership semantics when useful:

```ts
const customersById = new Map();
const selectedProductIds = new Set();
const processedOrderIds = new Set();
```

Use `processed` only when membership genuinely means that processing has occurred; do not use it as an unspecified transformation label.

### Booleans

Choose names that distinguish current state, capability, policy, requirement, and completed history:

```ts
const isCheckoutLoading = false;
const hasLoadedCheckout = false;
const canSubmitCheckout = true;
const shouldRetryPayment = false;
const didCompleteCheckout = false;
```

### Functions

Name the observable contract at the same abstraction level as its callers:

```ts
calculateOrderTotal()
validateShippingAddress()
fetchCustomerOrders()
canCancelOrder()
```

Avoid `process`, `handle`, `execute`, or `run` when a more precise action is supported by the behavior. These words remain valid when they are the established domain operation.

Keep the declaration honest about side effects. A query-like name must not conceal creation, persistence, publication, deletion, or external communication. Use `handle` for a real event, request, command, or failure boundary rather than as a generic prefix for all business logic.

Inside the callable, align parameters and local bindings with the declaration's vocabulary. Name meaningful transformations by their resulting state, accumulators by their invariant when needed, and callback elements as singular members of their collection. Read `function-and-local-naming.md` for the full callable and intrafunction decision model.

### Errors and Results

Keep the failing operation or domain concept visible when multiple operations coexist:

```ts
customerOrdersError
paymentAuthorizationResult
shippingAddressValidationErrors
```

Do not expand a tiny scope solely to avoid `error` or `result` when no ambiguity exists.

## 5. Perform a Silent Semantic Pass

Before completing the code:

1. Re-read important names without relying on their declarations.
2. Check entity/ID, singular/plural, boolean, unit, state, and representation distinctions.
3. Check that callable declarations, parameters, callback or closure bindings, accumulators, derived values, errors, and returns form one coherent semantic narrative.
4. Remove type words and redundant scope.
5. Replace vague transformation labels with the resulting semantic state.
6. Confirm that terminology and surface form match the surrounding codebase and target ecosystem.
7. Shorten any name that can lose a word without becoming ambiguous in that ecosystem.

Do this silently. Return the requested implementation rather than a separate naming essay unless the user asks for rationale.

## Avoid Over-Naming

Prefer:

```ts
const activeOrganizationUsers = organizationUsers.filter(
  (user) => user.isActive,
);
```

Avoid:

```ts
const currentlyActiveUsersBelongingToTheSelectedOrganization =
  organizationUsers.filter((organizationUser) => organizationUser.isActive);
```

The longer version repeats information that the scope and collection already communicate.

## Completion Invariants

- Important names express domain meaning rather than storage type.
- Function and method names match their observable contract, including important effects.
- Parameters and local variables make meaningful data-flow stages clear without over-naming tiny scopes.
- Meaningful transformations are visible in derived values.
- Related identifiers use one vocabulary.
- Potentially dangerous units or representations are explicit.
- Conventional short locals remain short.
- Casing, visibility, predicate style, and public API form are idiomatic for the target language.
- No protected external contract was renamed for style.
