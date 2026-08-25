# Callable and Parameter Naming

Name callables from their observable contract: caller input, result, effects, failures, and guarantees across every reachable path.

## Contract Shape

- Commands reveal their domain effect: authorize, persist, publish, cancel, reserve.
- Queries and computations do not hide creation, mutation, publication, deletion, or remote I/O.
- Predicates distinguish state, history, capability, policy, requirement, and support; expose `any`/`all` quantifiers when collection truth would otherwise be misread.
- Conversions respect ecosystem meanings for `as`, `to`, `into`, `from`, `try`, `parse`, encode, decode, and allocation.
- Handlers name the stimulus or boundary; business operations need not become `handle...`.
- Orchestrators name the workflow or outcome, not a list of implementation verbs.

Use repository conventions before generic verb guidance. Where no stronger convention exists, `find` can imply absence, `list` a collection, `fetch` remote or asynchronous I/O, `read` local storage or a stream, `calculate` a computation, `build` construction without persistence, and `resolve` selection from rules or candidates.

## Parameters and Labels

Parameters describe what callers provide, not merely their type. Distinguish entities from IDs, singular from collections, and dangerous units or representations. Public names and argument labels can be contracts. Signature redesign, options objects, overloads, and API migration require separate authorization.

## Review as One Unit

Inspect signature, all return/effect paths, failures, callers, tests, overrides, protocols, reflection, and consumers. Align parameters, meaningful locals, errors, results, and effects as one family. Preserve the declaration when an alternative only adds words.
