# Java, Kotlin, C#, Swift, and Dart Patterns

Apply these patterns to JVM, .NET, Apple-platform, and Dart code after inspecting the repository's language version, API guidelines, analyzers, and framework conventions. Public members, parameter labels, annotations, overrides, serialization names, and generated bindings can be contracts.

## Shared Object-Oriented and Mobile Concerns

Distinguish domain roles without repeating type information:

```text
Customer
CustomerId
CreateOrderRequest
OrderResponse
PaymentEvent
ValidationError
```

Role suffixes are useful when they distinguish real API or architectural boundaries. Avoid automatic suffixes such as `Object`, `Class`, `Manager`, `Helper`, `Util`, or `Data` when they hide the actual responsibility.

Before renaming, inspect:

- interfaces, protocols, base classes, overrides, and implementations;
- reflection, annotations, attributes, dependency injection, and code generation;
- serializers, ORMs, UI bindings, and route names;
- public constructor and method parameter names;
- platform interop and Objective-C, JNI, native, or COM boundaries;
- asynchronous API naming conventions;
- source and binary compatibility expectations.

## Java

Follow project and framework conventions for packages, types, methods, fields, constants, records, and generic parameters.

- Prefer domain nouns for classes and records.
- Prefer precise actions or predicates for methods.
- Keep collection elements and collection names semantically aligned.
- Use `Dto`, `Request`, `Response`, `Entity`, or `Event` only when the role is real and useful.
- Do not repeat the enclosing type in every member name.

Example:

```java
List<Order> pendingOrders = orderRepository.findPendingByCustomerId(customerId);
```

Overrides, bean properties, framework lifecycle methods, reflection-based names, record components, JSON fields, JPA mappings, dependency-injection qualifiers, and published method parameters may constrain renames.

## Kotlin

Use Kotlin's property, extension, nullability, coroutine, and sealed-type idioms rather than translating Java mechanically.

- Name properties by domain meaning without `get` or `set` prefixes unless an API convention requires them.
- Boolean properties should read as predicates according to the codebase convention.
- Distinguish nullable candidates, validated values, and required values only when multiple states coexist.
- Extension functions should reveal the capability or transformation they add.
- Sealed types and enum entries should name domain states or events precisely.

Named arguments make parameter names part of source-level API usage. Treat public parameter renames as compatibility-sensitive. Preserve serialization annotations, Compose state contracts, platform declarations, and generated members.

## C# and .NET

Respect the distinction between public API form and local-variable form.

- Public types, members, and properties normally follow the project's public naming convention.
- Locals and parameters follow the local convention without type prefixes.
- Predicate properties and methods should communicate state, capability, or result clearly.
- `Try` should preserve the established success/failure contract.
- An `Async` suffix can be meaningful in .NET APIs when it distinguishes task-returning operations according to repository convention; do not remove or add it mechanically.
- Cancellation tokens, event handlers, dependency properties, commands, and binding names can follow framework conventions.

Example:

```csharp
public Task<IReadOnlyList<Order>> FetchPendingOrdersAsync(
    CustomerId customerId,
    CancellationToken cancellationToken);
```

Attributes, reflection, serializers, Entity Framework mappings, Razor bindings, XAML names, COM-visible members, and public parameter names require contract analysis.

## Swift

Swift API meaning can span the base name and argument labels. Review the complete call site, not only the declaration.

- Types and protocols should communicate domain roles or capabilities.
- Methods and argument labels should read naturally at the call site.
- Boolean properties should read as assertions about the receiver.
- Distinguish mutating actions from value-returning transformations according to local API design.
- Do not add `Async` merely because a method uses Swift concurrency unless the API convention requires it.

Example call-site intent:

```swift
orderRepository.pendingOrders(for: customerID)
```

Argument labels, protocol requirements, overrides, `Codable` keys, Objective-C selectors, notifications, storyboard or SwiftUI bindings, asset names, and generated interfaces may be external contracts.

## Dart and Flutter

Follow Dart analyzer and repository conventions for libraries, types, members, locals, constants, and private identifiers.

- Domain types and widgets should communicate their role without automatic `Widget` or `Manager` suffixes unless the role distinction helps.
- A leading underscore has library-private meaning and should not be changed casually.
- Named parameters are part of call-site readability and can be public API.
- Futures and streams should be named by the value or event sequence they represent, not merely `futureData` or `streamData`.
- State, controllers, callbacks, routes, serialization fields, and generated code require framework-aware analysis.

Example:

```dart
final pendingOrders = await orderRepository.fetchPendingOrders(customerId);
```

## Review Checklist

- Does the name match the target language's public, private, property, and callable conventions?
- Are overrides, protocol members, named parameters, argument labels, and async conventions preserved?
- Are reflection, annotations, serialization, ORM, UI binding, and interop contracts protected?
- Do role suffixes communicate actual boundaries rather than vague architecture?
- Are nullability, result, event, and lifecycle distinctions explicit only when they matter?
- Does the call site remain natural and semantically continuous across layers?
