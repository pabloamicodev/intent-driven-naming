# Data handling and minimization

The skill can analyze proprietary code, so benchmark and deployment operators must treat source,
prompts, model output, artifacts, and usage metadata as potentially confidential.

## Minimum necessary context

Load only the declaration, relevant data-flow slice, callers and consumers needed to establish
meaning, plus strings or configuration needed to find dynamic contracts. Prefer symbol graphs,
language-server references, AST queries, and bounded snippets over copying a repository. Do not send
secrets, production records, credentials, unrelated files, or full histories to an external model.

Acquire context in stages: declaration/type/scope first; assignments, branches, reads, and focused
tests only if needed; callers and the semantic family only for a plausible material change; complete
boundary coverage only before applying a changing decision. Stop at `keep` or `defer` as soon as the
evidence supports it. This minimizes disclosure as well as tokens.

`loaded_resources` records only repository-relative skill resource names. Evaluation artifacts use
sanitized bundles and content hashes; sensitive filenames, binary content, and high-confidence token
or private-key signatures are rejected without echoing the secret. They must not contain credentials or absolute developer paths.
Private benchmark cases and raw external results belong in ignored directories or an access-
controlled evidence store.

JSONL evaluation records are streamed with hard per-record and 256 MiB cumulative byte ceilings
before decoding, so an oversized or malformed artifact cannot force an unbounded read. Operators
should impose a smaller runner limit when their data policy requires it.

## External processing

Before using a hosted model, operators must confirm authorization, retention settings, geographic
and contractual requirements, and whether code may be used for training. Local or approved private
execution is required when policy prohibits external processing. Provider credentials stay in the
host environment and never enter datasets, result JSONL, review packets, logs, or commits.

Experiment manifests contain hashes and public identities only. Runner configurations map those identities to local paths and command arrays; credentials still come only from the host environment. Evidence ledgers record the runner-configuration hash, not its command contents. Keep local runner configurations private when paths or operational metadata are sensitive.

## Retention and publication

Retain the smallest evidence needed to reproduce a claim: configuration hashes, pinned versions,
aggregate metrics, sanitized outputs, reviewer labels, and checksums. Public evidence must redact
source and personal data. Reviewers receive opaque candidate IDs; reidentification keys remain
separate and access-controlled. Deletion and retention periods follow the code owner's policy.

The repository validator checks structure, not organizational authorization. A valid artifact is
not proof that its collection or publication was permitted.
