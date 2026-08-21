# TypeScript, JavaScript, and Web Framework Patterns

Apply these patterns to TypeScript, JavaScript, Node.js, browser code, and component frameworks. Existing project, framework, generated-code, and public API conventions remain authoritative.

## Variables and Derived Values

Prefer domain entities and resulting states:

```ts
const users = await fetchUsers();
const activeUsers = users.filter((user) => user.isActive);
const activeUserIds = activeUsers.map((user) => user.id);
```

For maps, sets, and indexes, expose the key or membership meaning:

```ts
const usersById = new Map(users.map((user) => [user.id, user]));
const selectedUserIds = new Set<string>();
const completedOrderIds = new Set<string>();
```

Avoid `userMap` when the key is important and not obvious.

## Callback Parameters

Preserve entity identity:

```ts
products
  .filter((product) => product.isAvailable)
  .map((product) => product.name);
```

Nested callbacks should keep distinct concepts visible:

```ts
organizations.map((organization) =>
  organization.members.map((member) => ({
    organizationId: organization.id,
    memberId: member.id,
  })),
);
```

Short accumulator names are acceptable in small, obvious numeric reducers. Use a semantic accumulator when the reduction has domain meaning:

```ts
const pendingOrdersTotal = pendingOrders.reduce(
  (totalInCents, order) => totalInCents + order.totalInCents,
  0,
);
```

## JavaScript and Node.js Conventions

Preserve conventional framework locals when their scope is obvious:

```ts
function middleware(req, res, next) {
  next();
}
```

Do not expand `req`, `res`, `next`, `ctx`, `event`, or `error` mechanically. Improve them when several requests, responses, contexts, events, or errors coexist and the domain distinction matters.

Do not rename dynamic property keys, CommonJS or ESM exports, package entry points, command names, environment keys, or JSON fields without checking consumers. Private fields, symbols, and module-local aliases may use clearer internal names while preserving the boundary.

Prefer operation semantics over automatic `Async` suffixes. Use `Async` only when the repository or API distinguishes synchronous and asynchronous variants that way.

## React State

State getters and setters must remain semantically aligned:

```tsx
const [searchQuery, setSearchQuery] = useState("");
const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
const [isCheckoutModalOpen, setIsCheckoutModalOpen] = useState(false);
```

Distinguish current activity from completed history and capability:

```tsx
const [isCheckoutLoading, setIsCheckoutLoading] = useState(false);
const [hasLoadedCheckout, setHasLoadedCheckout] = useState(false);
const canSubmitCheckout = isFormValid && !isCheckoutLoading;
```

Do not rename a setter independently from its state value.

## Props and Callbacks

Name callback props by the event or completed intent from the component consumer's perspective:

```tsx
type CheckoutFormProps = {
  onCheckoutSubmit: (request: CheckoutRequest) => void;
  onShippingAddressChange: (address: ShippingAddress) => void;
};
```

Inside the component, a handler can describe its local responsibility:

```tsx
function handleCheckoutSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  onCheckoutSubmit(checkoutRequest);
}
```

When no local handler behavior exists, pass the domain action directly:

```tsx
<Button onClick={openCheckoutModal}>Checkout</Button>
```

Avoid `handleClick`, `handleChange`, and `handleSubmit` when multiple actions or domain-specific intent make them ambiguous.

## React Query and Other Async State

In a small scope with one query, library property names may remain clear:

```tsx
const customerOrdersQuery = useQuery(customerOrdersOptions);
```

When destructuring multiple query results, preserve the domain family:

```tsx
const {
  data: customerOrders,
  error: customerOrdersError,
  isLoading: areCustomerOrdersLoading,
} = useQuery(customerOrdersOptions);
```

Grouping is often clearer when the library exposes many related fields:

```tsx
const customerOrdersQuery = useQuery(customerOrdersOptions);

customerOrdersQuery.data;
customerOrdersQuery.error;
customerOrdersQuery.isLoading;
```

Choose the pattern that reduces collisions and keeps the component readable. Do not alias every library field mechanically.

## Vue, Svelte, and Angular

Keep framework concepts visible without restating the framework in every name:

- Vue refs and computed values should express their domain state; do not add `Ref` merely to restate the wrapper type unless competing representations require it.
- Svelte store names should preserve the domain concept across the store and its auto-subscription form; `# TypeScript, JavaScript, and Web Framework Patterns

Apply these patterns to TypeScript, JavaScript, Node.js, browser code, and component frameworks. Existing project, framework, generated-code, and public API conventions remain authoritative.

## Variables and Derived Values

Prefer domain entities and resulting states:

```ts
const users = await fetchUsers();
const activeUsers = users.filter((user) => user.isActive);
const activeUserIds = activeUsers.map((user) => user.id);
```

For maps, sets, and indexes, expose the key or membership meaning:

```ts
const usersById = new Map(users.map((user) => [user.id, user]));
const selectedUserIds = new Set<string>();
const completedOrderIds = new Set<string>();
```

Avoid `userMap` when the key is important and not obvious.

## Callback Parameters

Preserve entity identity:

```ts
products
  .filter((product) => product.isAvailable)
  .map((product) => product.name);
```

Nested callbacks should keep distinct concepts visible:

```ts
organizations.map((organization) =>
  organization.members.map((member) => ({
    organizationId: organization.id,
    memberId: member.id,
  })),
);
```

Short accumulator names are acceptable in small, obvious numeric reducers. Use a semantic accumulator when the reduction has domain meaning:

```ts
const pendingOrdersTotal = pendingOrders.reduce(
  (totalInCents, order) => totalInCents + order.totalInCents,
  0,
);
```

## JavaScript and Node.js Conventions

Preserve conventional framework locals when their scope is obvious:

```ts
function middleware(req, res, next) {
  next();
}
```

Do not expand `req`, `res`, `next`, `ctx`, `event`, or `error` mechanically. Improve them when several requests, responses, contexts, events, or errors coexist and the domain distinction matters.

Do not rename dynamic property keys, CommonJS or ESM exports, package entry points, command names, environment keys, or JSON fields without checking consumers. Private fields, symbols, and module-local aliases may use clearer internal names while preserving the boundary.

Prefer operation semantics over automatic `Async` suffixes. Use `Async` only when the repository or API distinguishes synchronous and asynchronous variants that way.

## React State

State getters and setters must remain semantically aligned:

```tsx
const [searchQuery, setSearchQuery] = useState("");
const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
const [isCheckoutModalOpen, setIsCheckoutModalOpen] = useState(false);
```

Distinguish current activity from completed history and capability:

```tsx
const [isCheckoutLoading, setIsCheckoutLoading] = useState(false);
const [hasLoadedCheckout, setHasLoadedCheckout] = useState(false);
const canSubmitCheckout = isFormValid && !isCheckoutLoading;
```

Do not rename a setter independently from its state value.

## Props and Callbacks

Name callback props by the event or completed intent from the component consumer's perspective:

```tsx
type CheckoutFormProps = {
  onCheckoutSubmit: (request: CheckoutRequest) => void;
  onShippingAddressChange: (address: ShippingAddress) => void;
};
```

Inside the component, a handler can describe its local responsibility:

```tsx
function handleCheckoutSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  onCheckoutSubmit(checkoutRequest);
}
```

When no local handler behavior exists, pass the domain action directly:

```tsx
<Button onClick={openCheckoutModal}>Checkout</Button>
```

Avoid `handleClick`, `handleChange`, and `handleSubmit` when multiple actions or domain-specific intent make them ambiguous.

## React Query and Other Async State

In a small scope with one query, library property names may remain clear:

```tsx
const customerOrdersQuery = useQuery(customerOrdersOptions);
```

When destructuring multiple query results, preserve the domain family:

```tsx
const {
  data: customerOrders,
  error: customerOrdersError,
  isLoading: areCustomerOrdersLoading,
} = useQuery(customerOrdersOptions);
```

Grouping is often clearer when the library exposes many related fields:

```tsx
const customerOrdersQuery = useQuery(customerOrdersOptions);

customerOrdersQuery.data;
customerOrdersQuery.error;
customerOrdersQuery.isLoading;
```

Choose the pattern that reduces collisions and keeps the component readable. Do not alias every library field mechanically.

 syntax is framework meaning, not a naming defect.
- Angular inputs, outputs, template references, selectors, and dependency-injection tokens can form public or runtime contracts. Improve internal aliases or handlers without silently changing those bindings.
- Across component frameworks, event props and handlers should describe domain intent when multiple actions coexist.

## Components and Hooks

Components normally use a domain noun or role:

```text
CustomerOrdersPanel
CheckoutSummary
ShippingAddressForm
```

Hooks should identify the capability, resource, or state they expose:

```text
useCustomerOrders
useCheckoutValidation
usePaymentAuthorization
```

Avoid `useData`, `useHandler`, or `useLogic` when a domain capability is known.

## Types, Interfaces, and Generics

Name types by the concept or contract role, not with an automatic `Type` or `Interface` suffix:

```ts
type Customer = { id: string };
type CheckoutOptions = { currency: CurrencyCode };
type PaymentAuthorizationResult = { isAuthorized: boolean };
```

Role suffixes are useful when they distinguish real boundaries:

```text
CreateOrderRequest
OrderResponse
UserDto
PaymentEvent
ValidationError
```

Conventional generic names are appropriate in tiny generic abstractions:

```ts
function identity<T>(value: T): T {
  return value;
}
```

Use domain generics when several type parameters or a public abstraction would otherwise be unclear:

```ts
type Repository<TEntity, TId> = {
  findById(id: TId): Promise<TEntity | null>;
};
```

## Async Function Names

Do not add `Async` merely because a TypeScript function returns a promise. Use it only when the repository convention or an API needs to distinguish synchronous and asynchronous variants.

Prefer names that reveal the operation:

```ts
fetchCustomerOrders()
authorizePayment()
persistCheckoutSession()
```

## Error and Event Names

Keep the operation or domain source visible when multiple errors or events coexist:

```ts
customerOrdersError
paymentAuthorizationError
checkoutSubmittedEvent
shippingAddressChangedEvent
```

Preserve third-party and browser event names at the boundary. Improve local aliases or handler names rather than changing the external event contract.

## Browser and Web Contracts

Preserve DOM property names, event types, custom-event names, data attributes, CSS selectors, form field names, URL parameters, storage keys, and postMessage payload fields when they form browser or integration contracts.

Map them to clearer internal names when useful:

```ts
const customerId = searchParams.get("customer_id");
```

Do not rename a visible HTML or CSS hook as though it were a private TypeScript variable.

## TypeScript and JavaScript Review Checklist

- Are array elements singular and collections plural?
- Do maps and sets reveal their key or membership semantics when needed?
- Are state and setter pairs synchronized?
- Do booleans distinguish activity, history, capability, and policy?
- Are query families distinguishable when several queries coexist?
- Do callbacks and handlers express domain intent?
- Do components and hooks expose their capability or resource?
- Are request, response, DTO, event, and error suffixes describing real roles?
- Are generic type parameters proportionate to their scope?
- Are external props, payloads, event names, DOM hooks, routes, and storage keys preserved?
- Are Node.js and framework-conventional locals kept proportionate to their scope?
- Are Vue refs, Svelte stores, Angular bindings, and React state families named by domain meaning rather than wrapper type?
