# Web Framework Patterns

Use this profile only when a task touches React, React Query, Vue, Svelte, Angular, or comparable component-framework contracts. Read it together with `typescript-javascript.md` when the implementation uses TypeScript or JavaScript.

## Component State

Keep state values and their mutation APIs semantically aligned:

```tsx
const [searchQuery, setSearchQuery] = useState("");
const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
const [isCheckoutModalOpen, setIsCheckoutModalOpen] = useState(false);
```

Distinguish current activity, completed history, and capability:

```tsx
const [isCheckoutLoading, setIsCheckoutLoading] = useState(false);
const [hasLoadedCheckout, setHasLoadedCheckout] = useState(false);
const canSubmitCheckout = isFormValid && !isCheckoutLoading;
```

Do not rename a setter, reducer action, store mutation, ref, or signal independently from the value or event family it represents.

## Props, Inputs, Outputs, and Callbacks

Name callback props from the component consumer's perspective:

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

When no local handling exists, pass the domain action directly. Avoid generic `handleClick`, `handleChange`, and `handleSubmit` when several actions make them ambiguous.

Treat component props, Angular inputs and outputs, Svelte exports, Vue emits, template references, selectors, and dependency-injection tokens as public or runtime contracts when consumers depend on their spelling.

## Query and Async State Families

One grouped query object is often clear:

```tsx
const customerOrdersQuery = useQuery(customerOrdersOptions);
```

When destructuring several query results, preserve each domain family:

```tsx
const {
  data: customerOrders,
  error: customerOrdersError,
  isLoading: areCustomerOrdersLoading,
} = useQuery(customerOrdersOptions);
```

Do not alias every library field mechanically. Alias or group when collisions, distance, or multiple queries make the domain relationship unclear.

## Vue, Svelte, and Angular

- Vue refs, reactive values, and computed values should express domain state; do not add `Ref` merely to restate the wrapper type.
- Svelte stores should preserve the domain concept across the store and its auto-subscription form; the `$` syntax is framework meaning, not a naming defect.
- Angular bindings, selectors, template variables, lifecycle hooks, and injection tokens may be public or dynamically resolved contracts.
- Signals, observables, stores, and reducers should retain one domain vocabulary across their value, update, error, and status families.

## Components, Hooks, and Composables

Components normally use a domain noun or role:

```text
CustomerOrdersPanel
CheckoutSummary
ShippingAddressForm
```

Hooks and composables should identify the capability, resource, or state they expose:

```text
useCustomerOrders
useCheckoutValidation
usePaymentAuthorization
```

Avoid `useData`, `useHandler`, `useLogic`, `Helper`, or `Manager` when a domain capability is known. Preserve framework-required prefixes and lifecycle names.

## Review Checklist

- Are state, setters, reducer actions, stores, signals, and derived values synchronized?
- Do booleans distinguish activity, history, capability, and policy?
- Are query families distinguishable when several queries coexist?
- Do callbacks and handlers express domain intent from the correct perspective?
- Do components, hooks, and composables expose their capability or resource?
- Are props, emits, bindings, selectors, template hooks, and injection tokens protected as contracts?
- Are framework concepts visible without repeating wrapper types in every name?
