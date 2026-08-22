# Private held-out evaluation

Public cases prevent regressions but can become familiar to model builders. Organization-grade
claims therefore require a private, access-controlled suite that is never committed or included in
agent context.

Store private activation and behavior JSONL outside the repository or under ignored
`evals/private/`. Validate it against the public case schema, use unique IDs in an operator-owned
namespace, freeze its hash before runs, and disclose only aggregate strata and cryptographic hashes.
Case authors and benchmark operators should be distinct from candidate implementers where possible.

The held-out suite must include ordinary generation, no-op audits, misleading callables and locals,
dynamic and generated boundaries, public and stateful migrations, security/trust stages,
distributed state, time bases, data/ML representations, observability contracts, and multilingual
requests. It must also include hard negatives that mention code while explicitly excluding naming.

Do not tune instructions on held-out failures. Move a case into the public development set before
using it to change the skill, then replace it with a fresh private case. Preserve raw results and
review keys in an approved evidence store, never in a public pull request.
