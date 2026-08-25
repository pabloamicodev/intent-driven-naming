# Managed and Mobile Language Exceptions

For Java, Kotlin, C#, Swift, and Dart, distinguish public API form from local form and inspect interfaces, protocols, overrides, reflection, annotations, serializers, ORMs, dependency injection, UI binding, code generation, and native interop.

Public parameter names and argument labels can be compatibility surfaces. Kotlin and Swift call-site semantics may span properties, base names, and labels. C# `Try` and `Async` forms can encode established contracts. Dart named parameters and library-private underscores affect API use. Preserve Java records, bean properties, framework lifecycle names, and generated members.

Use DTO, request, response, entity, event, command, options, or error suffixes only when they identify a real role. Do not add `Manager`, `Helper`, `Util`, `Object`, or `Data` to conceal responsibility.

Check source compatibility, binary compatibility, serialization, platform selectors, notifications, routes, and bindings separately from local symbol references.
