# Dynamic Language Exceptions

Apply repository conventions for Python, Ruby, PHP, and comparable languages. Dynamic lookup, metaprogramming, decorators, annotations, serializers, ORMs, templates, registries, and monkey-patching can turn spelling into runtime behavior.

Public parameter names are source-level contracts when callers bind by keyword. Preserve Python magic names and protocol methods, Ruby predicates/bang semantics and DSL vocabulary, and PHP framework/container/attribute conventions.

Do not add type words merely because static types are absent. Use domain roles, state, representation, units, and effects only where context does not already communicate them. Keep conventional receiver, block, exception, and iterator names in compact scopes.

Search strings and framework metadata separately from symbol references. Prefer aliases, serializer mappings, or wrappers when external field names remain fixed. If runtime dispatch cannot be traced, `defer` is safer than a speculative rename.
