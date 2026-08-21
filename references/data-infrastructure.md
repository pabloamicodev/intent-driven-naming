# Data, Schema, Shell, and Infrastructure Patterns

Apply these patterns to SQL, analytics and data pipelines, schemas, shell scripts, PowerShell, configuration, and infrastructure as code. In these artifacts, a rename can affect persisted data, state addresses, CLI interfaces, dashboards, automation, or external consumers even when no compiled symbol changes.

## SQL and Database Schemas

Follow the existing database and dialect convention for casing, quoting, singular or plural relation names, constraints, indexes, procedures, parameters, and aliases.

New schema identifiers should expose correctness-critical meaning:

```sql
price_in_cents
request_timeout_ms
customer_id
authorized_at_utc
```

Existing tables, columns, constraints, indexes, views, functions, triggers, and migration identifiers are persisted or operational contracts. Do not rename them as an ordinary code refactor.

Use query aliases to translate legacy schema vocabulary locally:

```sql
SELECT
  cust_id AS customer_id,
  price AS price_in_cents
FROM legacy_orders;
```

Verify that the alias does not misrepresent the stored unit or domain meaning.

In complex queries, name CTEs and aliases by their semantic stage:

```text
eligible_customers
pending_orders
monthly_revenue_by_customer
```

Avoid `data`, `temp`, `cte1`, and `final_result` when the relation has a stable business meaning. Short table aliases remain acceptable when joins are small and unambiguous.

## Data Pipelines and Analytics

Distinguish source, representation, validation, grain, window, and unit when they affect interpretation:

```text
raw_orders
validated_orders
daily_order_totals
revenue_usd
customers_by_region
```

Column names, dataframe fields, feature names, model inputs, metric names, warehouse relations, and dashboard dimensions can be cross-system contracts. Improve local bindings without silently changing downstream schemas.

Avoid using `clean`, `processed`, or `final` as a substitute for the transformation. Prefer names such as `deduplicated_customers`, `normalized_phone_numbers`, or `orders_with_customer_segments`.

Preserve the data grain in names when multiple grains coexist, for example order-level versus customer-level totals.

## API and Interface Schemas

OpenAPI, GraphQL, Protocol Buffers, Avro, JSON Schema, and similar definitions create public or generated contracts.

- For new fields, use clear domain meaning and units.
- For existing fields, plan compatibility, aliases, deprecation, versioning, or migration explicitly.
- Preserve field numbers, serialized names, union tags, operation IDs, and generated-code expectations.
- Do not “fix” generated client names without changing the durable schema or generator configuration.

## Shell Scripts

Shell conventions vary by shell and repository. Distinguish exported environment variables, script constants, local variables, functions, positional parameters, and command-line flags.

In common shell code:

- uppercase names often imply exported environment values or constants;
- lowercase names can keep local bindings visually distinct;
- conventional status, iterator, and path locals can remain short in narrow scopes;
- quoting and expansion behavior matter more than stylistic renaming.

Environment variables, CLI flags, subcommands, filenames, and external command options are interfaces. Do not rename them without coordinating their consumers.

## PowerShell

Respect PowerShell's command and parameter conventions:

- cmdlet and advanced-function names commonly use an established `Verb-Noun` form;
- public parameter names are user-facing API and can be used by name;
- automatic variables, preference variables, scopes, aliases, and provider paths have language meaning;
- local variables should express the domain without unnecessary type prefixes.

Preserve public command names and parameters unless the task includes compatibility aliases or a breaking CLI migration.

## Infrastructure as Code

Terraform, Pulumi, CloudFormation, Kubernetes, Helm, Ansible, and other infrastructure systems can persist logical identifiers or use them in state, imports, references, policies, and automation.

Distinguish:

- local labels used only inside one module;
- resource addresses stored in state;
- provider object names created remotely;
- output and variable names consumed by other modules;
- tags, labels, annotations, secret keys, and policy identifiers;
- generated manifests and templates.

A clearer Terraform resource label can still require a state move. A Kubernetes metadata name can change resource identity. A Helm value key can be a public configuration contract. Do not treat these as ordinary local-variable renames.

For new infrastructure, name resources by role and environment only when those distinctions are stable and required. Avoid encoding volatile deployment details into every identifier.

## Configuration Files

JSON, YAML, TOML, XML, dotenv, and framework configuration keys may be read by external tools or users. Preserve known keys and schema-defined names.

Internal anchors, aliases, locals, and template variables can improve when references are traceable. Do not infer that a key is private merely because it appears in one repository.

## Verification

Choose verification appropriate to the artifact:

- schema validation and compatibility checks;
- migration dry runs and rollback review;
- query tests and result-shape comparison;
- data-quality and grain checks;
- shell linting and targeted execution;
- PowerShell analysis and parameter compatibility;
- infrastructure plan, preview, policy, and state-address review;
- generated-code regeneration and diff review.

Do not claim a rename is behavior-preserving without checking the relevant persisted or operational surface.

## Review Checklist

- Are units, currencies, time bases, grain, and representation explicit where needed?
- Do query stages and pipeline outputs describe their transformation?
- Are schema fields, operation IDs, CLI parameters, environment keys, and serialized names protected?
- Have database migrations, infrastructure state, remote resource identity, and downstream data consumers been considered?
- Are aliases or adapters used when internal clarity can improve without changing a contract?
- Does the naming follow the actual dialect, shell, tool, and repository convention?
