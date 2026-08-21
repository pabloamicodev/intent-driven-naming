# Python, Ruby, and PHP Patterns

Apply these patterns to Python, Ruby, and PHP after inspecting the repository's formatter, linter, framework, and version conventions. Dynamic language does not mean weak semantics; names often carry distinctions that a compiler cannot enforce.

## Shared Dynamic-Language Risks

Inspect more than static references before renaming:

- reflection and attribute lookup;
- monkey patching and open classes;
- decorators, annotations, and metaprogramming;
- framework callbacks and convention-based discovery;
- ORM models and database-backed fields;
- serializer aliases and request parameters;
- dependency containers and string registrations;
- templates, route names, CLI commands, and configuration keys.

Preserve runtime-discovered names or map them explicitly at a boundary.

## Python

Follow project configuration and established Python style for casing and visibility. In conventional Python code:

- modules, functions, methods, and locals use `snake_case`;
- classes and exception types use `PascalCase`;
- constants use the project's constant convention;
- `self` and `cls` are semantic protocol names and should remain concise;
- a leading underscore communicates non-public intent by convention;
- double-underscore and dunder names can have language or framework meaning and must not be normalized casually.

Render boolean propositions idiomatically:

```py
is_authenticated
has_active_subscription
can_edit_profile
should_retry_payment
```

Keep comprehensions and tiny mathematical transforms proportionate:

```py
active_users = [user for user in users if user.is_active]
```

Do not replace `user` with a verbose phrase when the comprehension already establishes the entity.

Distinguish representations and units when they coexist:

```py
raw_phone_number = form_data["phone"]
normalized_phone_number = normalize_phone_number(raw_phone_number)
request_timeout_seconds = 30
```

Pydantic aliases, dataclass field metadata, Django or SQLAlchemy model fields, serializer fields, and keyword argument names may be public or persisted contracts. Prefer aliases and adapters over silent field renames.

## Ruby

Follow the repository and framework convention. Typical Ruby code uses:

- `snake_case` for methods and locals;
- `CamelCase` for classes and modules;
- predicate methods ending in `?`;
- a trailing `!` only when it communicates a meaningful dangerous, mutating, or exceptional counterpart according to the API convention;
- symbols, method names, and constants as potential runtime lookup keys.

Prefer predicates that read as questions:

```rb
authenticated?
active_subscription?
editable_by?(actor)
```

Do not add `is_` mechanically when the idiomatic `?` form is clearer.

Active Record attributes, route helpers, callbacks, scopes, serializers, and metaprogrammed method names may derive from schemas or framework conventions. A name that appears internal can still be generated or invoked dynamically.

Preserve block parameter clarity without over-expansion:

```rb
pending_orders.sum { |order| order.total_in_cents }
```

## PHP

Follow the project's supported PHP version, framework, and style rules. Common modern PHP conventions include:

- `camelCase` for methods, parameters, and locals;
- `PascalCase` for classes, interfaces, enums, and traits;
- role suffixes such as `Request`, `Response`, `Dto`, `Event`, or `Exception` only when they distinguish real contracts;
- semantic collection and unit names rather than type prefixes.

Avoid type-oriented names such as `$userArray`, `$orderObject`, or `$stringToken` when the type system and declaration already communicate that information.

Array keys and object properties can be serialized or dynamically accessed:

```php
$customerId = $payload['customer_id'];
```

Preserve the external key while improving the internal variable. Treat magic methods, framework lifecycle methods, container service IDs, route names, template variables, and ORM fields as possible contracts.

## Errors, Nullability, and Results

Dynamic code benefits from names that distinguish optional, failed, or unvalidated values when multiple representations coexist:

```text
candidate customer
validated customer
customer lookup error
parsed configuration
```

Do not add `maybe`, `optional`, `nullable`, or `result` solely to restate a clear local check. Add the distinction when it prevents a wrong use or separates simultaneous states.

## Review Checklist

- Does the casing match the actual language and repository rather than another ecosystem?
- Are `self`, `cls`, predicate suffixes, magic methods, and conventional block parameters preserved?
- Are ORM, serializer, route, template, and array-key contracts protected?
- Have reflection and metaprogramming references been considered?
- Are dynamic representations and units explicit where correctness depends on them?
- Are type words absent unless they describe a real architectural role?
