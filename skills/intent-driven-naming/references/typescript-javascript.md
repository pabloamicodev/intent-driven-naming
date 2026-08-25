# TypeScript and JavaScript Exceptions

Use repository casing and acronym rules. Do not add type suffixes to values whose static or local context is clear. Preserve meaningful distinctions among values, IDs, collections, promises, errors, events, and serialized forms.

Type names, interfaces, unions, generics, and branded IDs should express domain roles without automatic `Data`, `Object`, `Type`, or `Interface` suffixes. A role suffix such as request, response, DTO, event, options, or error is useful only when it marks a real boundary.

Do not append `Async` or `Promise` mechanically; follow project/API convention. Query-like names must not hide I/O or mutation. Event props, listener names, custom-element attributes, global browser keys, storage keys, and DOM selectors can be contracts.

Before renaming inspect object shorthand, destructuring aliases, dynamic property access, decorators, dependency injection, module exports, declaration files, source maps, and generated clients. Keep wire keys explicit when internal aliases improve.
