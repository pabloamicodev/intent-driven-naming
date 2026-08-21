# Callable and Parameter Naming

Name a function, method, constructor, command, query, handler, or callback API from its observable contract: caller input, result, effects, failures, and expectations.

## Contract Shape

- Commands reveal their domain effect: authorize, persist, publish, cancel, reserve.
- Queries and computations do not hide creation, mutation, publication, deletion, or remote I/O.
- Predicates distinguish state, history, capability, policy, requirement, and support.
- Conversions respect ecosystem meanings for `as`, `to`, `into`, `from`, `try`, `parse`, encode, decode, and allocation.
- Handlers name the stimulus or boundary; do not turn every business operation into `handle...`.
- Orchestrators name the business workflow or outcome, not a list of implementation verbs.

Use repository conventions before generic verb guidance. Where no stronger convention exists, `find` can imply absence, `list` a collection, `fetch` remote or asynchronous I/O, `read` local storage or a stream, `calculate` a computation, `build` construction without persistence, and `resolve` selection from rules or candidates.

## Parameters and Labels

Parameters describe what callers provide, not merely their type. Distinguish entities from IDs, singular values from collections, and dangerous units or representations. Public parameter names and argument labels are contracts in languages that support named calls. Signature redesign, options objects, overloads, and API migration require separate authorization.

## Review as One Unit

Inspect callers, signature, implementation, return paths, side effects, failures, tests, overrides, protocols, reflection, and public consumers. Confirm that parameters, meaningful locals, errors, returned values, and effects use one semantic family. Preserve the current declaration when an alternative only adds words.
