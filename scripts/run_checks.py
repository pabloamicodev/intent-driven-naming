#!/usr/bin/env python3
"""Run every offline repository and conformance check."""

from __future__ import annotations

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
    run("repository", [python, "scripts/validate_repository.py"])
    run("unit tests", [python, "-m", "unittest", "discover", "-s", "tests", "-v"])
    run("fixtures", [python, "harness/verify_fixtures.py"])
    print("\nall offline checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
