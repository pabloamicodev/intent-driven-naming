# High-Risk Semantic Distinctions

Load this reference only when these distinctions affect correctness or safety.

## Security and Privacy

Do not collapse raw, parsed, validated, sanitized, escaped, encoded, encrypted, authenticated, authorized, trusted, secret, and public values. Each word asserts a different guarantee. Derive the name from the transformation actually proven, not the next operation the developer intends to perform.

## Distributed and Concurrent State

Distinguish requested, accepted, persisted, committed, replicated, observed, acknowledged, and confirmed states when they coexist. Preserve idempotency keys, message tags, actor or process names, topics, locks, channels, ownership, captures, and shared mutable state as contracts or concurrency semantics.

## Time and Ordering

Expose duration units and distinguish wall-clock, monotonic, event, processing, ingestion, deadline, and expiration time when confusion is plausible. Include timezone or UTC only when not guaranteed by the type or contract.

## Data and Machine Learning

Preserve grain, source, window, currency, denominator, feature/label role, predicted/observed state, and train/validation/test partition where they affect interpretation. `clean`, `processed`, and `final` do not explain deduplication, normalization, filtering, aggregation, or leakage controls.

## Observability

Metric, log-field, trace-attribute, dashboard, and alert names can be persisted cross-system contracts. Preserve unit, aggregation, cardinality, and event semantics; do not rename them as locals without coordinating consumers.

## Resources and Performance

Distinguish length from capacity, allocated from reserved, owned from borrowed, cached from authoritative, hot from cold, and compressed from decoded only when both forms or a correctness risk exist. Naming normally does not improve runtime performance; never trade clarity for manual minification unless the external contract explicitly requires it.

When a guarantee is unproven or ownership is unclear, choose `defer` rather than encoding wishful semantics into the name.
