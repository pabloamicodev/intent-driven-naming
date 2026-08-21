# Web Framework Exceptions

Name state families by domain concept plus meaningful lifecycle distinction. Keep value, loading, error, selected, optimistic, stale, and submitted variants aligned without repeating the component name when scope already supplies it.

Distinguish callback props or registration points from local handlers according to framework convention. Preserve lifecycle hooks, reserved exports, dependency arrays, refs, signals, stores, reactive declarations, template bindings, route params, cache keys, form field names, test selectors, and server/client boundaries.

For query libraries, keep query keys, fetched values, errors, mutations, and invalidation targets as one semantic family. Do not turn every function into `handle...`, every state into `...State`, or every component into `...Component`.

Review emitted HTML attributes, serialized form data, hydration contracts, and framework-generated names separately from local bindings.
