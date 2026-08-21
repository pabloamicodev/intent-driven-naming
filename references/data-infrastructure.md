# Data and Infrastructure Exceptions

In SQL, schemas, pipelines, shell, PowerShell, configuration, and infrastructure, spelling often persists beyond compilation.

Expose unit, currency, time basis, grain, window, source, and transformation for new identifiers when a wrong reading matters. Name CTEs, frames, relations, and aggregates by semantic stage rather than `temp`, `data`, or `final`. Use aliases to translate legacy schema vocabulary without silently migrating storage.

Treat tables, columns, constraints, field numbers, operation IDs, event schemas, metric names, environment keys, CLI flags, PowerShell parameters, Terraform addresses, Kubernetes names, Helm values, outputs, and remote resource identities as contracts. Generated clients follow their authoritative schema or generator.

Respect shell scope/export conventions, PowerShell Verb-Noun APIs, SQL dialect rules, and tool-specific casing. Verification may require schema compatibility, query result-shape tests, data-grain checks, migration dry runs, infrastructure plans/state moves, shell analysis, and generated-code reproduction.
