# Types, Fields, Collections, and Messages

Use this when the declaration is not primarily a callable or local.

- Types name their domain abstraction, value, role, capability, policy, or state. `Manager`, `Helper`, `Info`, and `Data` are defects only when they hide responsibility.
- Fields name the held value and role. Do not repeat the containing type unless distant use or competing peers require it.
- Collections name membership and elements use the corresponding singular. Maps and indexes expose the key/value relation when types and scope do not.
- Enums name the varying dimension; variants name mutually exclusive values without stutter already supplied by ecosystem syntax.
- Constants name meaning, unit, basis, or policy—not their literal. Add units only when types cannot prevent a material misread.
- Errors name the failed operation or violated condition. Events/messages distinguish requests, facts, and lifecycle stage; a completed event cannot describe an attempt.
- Type parameters stay conventional and short when one role is obvious; distinguish swappable roles. Modules and namespaces contribute context, but external members remain searchable.

Review related declarations as a family, but change only material wrong reads. Generated, serialized, reflected, or persisted names remain contracts or explicit mappings.
