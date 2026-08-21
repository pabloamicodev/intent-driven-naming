# TypeScript and JavaScript Patterns

Use this profile for TypeScript, JavaScript, Node.js, and browser modules. Load `web-frameworks.md` only when the task actually touches React, Vue, Svelte, Angular, or component-framework APIs. Repository, generated-code, and public API conventions remain authoritative.

## Values and Collections

Prefer domain entities and resulting states:

```ts
const users = await fetchUsers();
const activeUsers = users.filter((user) => user.isActive);
const activeUserIds = activeUsers.map((user) => user.id);
```

Expose map keys or set membership when they matter:

```ts
const usersById = new Map(users.map((user) => [user.id, user]));
const selectedUserIds = new Set<string>();
```

Use plural collections and singular callback elements. Keep short accumulator names in tiny obvious reducers; name the invariant when the reduction has domain meaning or a unit:

```ts
const pendingOrdersTotalInCents = pendingOrders.reduce(
  (totalInCents, order) => totalInCents + order.totalInCents,
  0,
);
```

## JavaScript and Node.js Conventions

Preserve conventional locals when their scope is obvious:

```ts
function middleware(req, res, next) {
  next();
}
```

Do not expand `req`, `res`, `next`, `ctx`, `event`, or `error` mechanically. Improve them when several values of that role coexist and the domain distinction matters.

Treat dynamic property keys, CommonJS or ESM exports, package entry points, command names, environment keys, and JSON fields as potential contracts. Use clearer internal aliases while preserving boundary spellings.

## Types, Interfaces, and Generics

Name types by the concept or contract role, not with automatic `Type` or `Interface` suffixes:

```ts
type Customer = { id: string };
type CheckoutOptions = { currency: CurrencyCode };
type PaymentAuthorizationResult = { isAuthorized: boolean };
```

Suffixes such as `Request`, `Response`, `Dto`, `Event`, and `Error` are useful only when they distinguish real roles.

Conventional generic names fit tiny abstractions:

```ts
function identity<T>(value: T): T {
  return value;
}
```

Use domain generics when several parameters or a public abstraction would otherwise be unclear:

```ts
type Repository<TEntity, TId> = {
  findById(id: TId): Promise<TEntity | null>;
};
```

## Async Operations

Do not add `Async` merely because a function returns a promise. Use it when the repository or public API distinguishes synchronous and asynchronous variants that way.

Prefer operation semantics:

```text
fetchCustomerOrders
authorizePayment
persistCheckoutSession
```

## Errors and Events

Keep the operation or domain source visible when several errors or events coexist:

```text
customerOrdersError
paymentAuthorizationError
checkoutSubmittedEvent
```

Preserve third-party, Node.js, and browser event names at the boundary. Improve local aliases or handler names instead of silently changing the event contract.

## Browser Contracts

Preserve DOM property names, event types, custom-event names, data attributes, CSS selectors, form field names, URL parameters, storage keys, and `postMessage` payload fields when they form contracts.

Map fixed spellings to clear internal names:

```ts
const customerId = searchParams.get("customer_id");
```

Object shorthand can expose a local binding as a serialized key. Expand it explicitly when an internal rename must preserve the output:

```ts
const selectedCustomerId = customer.id;
return { customerId: selectedCustomerId };
```

## Review Checklist

- Are collections plural and elements singular?
- Do maps, sets, and accumulators expose relevant semantics and units?
- Are conventional Node.js locals proportionate to their scopes?
- Do types, generics, errors, and events describe real roles?
- Do async names follow repository API conventions rather than a blanket suffix rule?
- Are exports, dynamic keys, payload fields, browser hooks, routes, and storage keys preserved?
- Are property shorthand and destructuring checked before local renames?
