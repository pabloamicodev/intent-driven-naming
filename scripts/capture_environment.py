#!/usr/bin/env python3
"""Capture non-secret toolchain versions for benchmark reproduction."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from datetime import date
from pathlib import Path


def version(command: list[str]) -> str | None:
    executable = shutil.which(command[0])
    if executable is None:
        return None
    completed = subprocess.run(
        [executable, *command[1:]], capture_output=True, text=True, check=False, timeout=30
    )
    if completed.returncode != 0:
        return None
    return (completed.stdout or completed.stderr).strip().splitlines()[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = {
        "schema_version": "1.0",
        "recorded_at": date.today().isoformat(),
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "tools": {
            "python": platform.python_version(),
            "codex": version(["codex", "--version"]),
            "node": version(["node", "--version"]),
            "typescript": version(["tsc", "--version"]),
            "dotnet": version(["dotnet", "--version"]),
            "go": version(["go", "version"]),
            "rustc": version(["rustc", "--version"]),
            "javac": version(["javac", "-version"]),
            "terraform": version(["terraform", "version"]),
            "powershell": version(["pwsh", "--version"]),
            "git": version(["git", "--version"]),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote environment metadata to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
