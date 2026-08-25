#!/usr/bin/env python3
"""Run every offline repository and conformance check."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> None:
    print(f"\n[{label}] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    python = sys.executable
    run("generated evals", [python, "scripts/export_evals.py", "--check"])
    if importlib.util.find_spec("jsonschema") is not None:
        run("json schemas", [python, "scripts/validate_schemas.py"])
    else:
        print("\n[json schemas] skipped; install requirements-dev.txt for strict validation", flush=True)
    if importlib.util.find_spec("mypy") is not None:
        run("type check", [python, "-m", "mypy"])
    else:
        print("\n[type check] skipped; install requirements-dev.txt for strict type checking", flush=True)
    run("repository", [python, "scripts/validate_repository.py"])
    run(
        "rename plan",
        [
            python,
            "skills/intent-driven-naming/scripts/runtime/validate_rename_plan.py",
            "examples/rename-plan.json",
        ],
    )
    run("unit tests", [python, "-m", "unittest", "discover", "-s", "tests", "-v"])
    run("fixtures", [python, "harness/verify_fixtures.py"])
    print("\nall offline checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
