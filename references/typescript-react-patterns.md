# TypeScript, JavaScript, and React Patterns

Apply these patterns only when they improve meaning in the actual TypeScript, JavaScript, React, or React Query scope. Existing project conventions remain authoritative.

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

## TypeScript and React Review Checklist

- Are array elements singular and collections plural?
- Do maps and sets reveal their key or membership semantics when needed?
- Are state and setter pairs synchronized?
- Do booleans distinguish activity, history, capability, and policy?
- Are query families distinguishable when several queries coexist?
- Do callbacks and handlers express domain intent?
- Do components and hooks expose their capability or resource?
- Are request, response, DTO, event, and error suffixes describing real roles?
- Are generic type parameters proportionate to their scope?
- Are external props, payloads, and event names preserved?
