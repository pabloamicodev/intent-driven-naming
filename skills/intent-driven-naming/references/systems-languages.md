# Systems Language Exceptions

For Go, Rust, C, and C++, preserve ecosystem conventions for packages, receivers, visibility, ownership, lifetimes, mutation, fallibility, conversions, linkage, and resource management.

Go favors concise package-aware names, consistent short receivers, conventional `err`, and initialism rules. Avoid getter prefixes unless the project requires them. Rust conversion prefixes and suffixes can encode borrowing, consumption, fallibility, or allocation; do not treat them as synonyms. In C/C++, investigate prefixes before removing them because they may mark ABI, subsystem, ownership, linkage, or generated roles.

Correctness-critical distinctions can include length/capacity, owned/borrowed, source/destination, checked/unchecked, and units. Add them only when competing forms or a wrong reading exist.

Protect exported symbols, ABI/FFI names, macros, tags, linker-visible names, function-pointer registrations, generated bindings, build variables, and platform entry points. Compile and test each affected target; one host platform is not proof of binary compatibility.
