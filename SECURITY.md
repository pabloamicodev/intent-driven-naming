# Security Policy

Naming refactors can affect public APIs, serialization, reflection, generated code, ABI surfaces, infrastructure state, and runtime registration. Reports that demonstrate an unsafe rename or a bypass of a contract-safety hard gate are treated as security-relevant.

## Supported Versions

Security fixes are provided for the latest released major version. Critical fixture or harness vulnerabilities may also receive a patch for the previous major version when practical.

## Reporting

Use the repository host's private vulnerability-reporting or security-advisory feature. Do not open a public issue for an unpatched vulnerability that could cause destructive refactors, credential exposure, arbitrary command execution, or benchmark-data disclosure.

Include:

- affected version and commit;
- minimal reproduction;
- language, agent, and environment;
- expected protected contract;
- observed unsafe behavior;
- whether the issue affects the skill instructions, harness, adapter protocol, or fixtures.

The maintainers should acknowledge a complete report within seven days, provide an initial severity assessment, and coordinate disclosure after a fix or documented mitigation is available.

## Harness Trust Boundary

Evaluation adapters are external executables. Review them before use, run them with least privilege, keep credentials in the host environment, and isolate candidate repositories. This project does not make an arbitrary third-party adapter safe.
