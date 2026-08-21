#!/usr/bin/env python3
"""Verify reference or generated fixture candidates in isolated subprocesses."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "evals" / "fixtures"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"


def render_command(parts: list[str], candidate: Path) -> list[str]:
    replacements = {
        "{python}": sys.executable,
        "{candidate}": str(candidate.resolve()),
    }
    return [replacements.get(part, part) for part in parts]


def verify_fixtures(candidate_root: Path | None, strict_tools: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    for fixture in manifest["fixtures"]:
        directory = FIXTURE_ROOT / fixture["directory"]
        if candidate_root:
            candidate = candidate_root / fixture["directory"] / fixture["candidate_filename"]
        else:
            candidate = directory / fixture["reference"]
        required_tool = fixture.get("required_tool")
        if required_tool and shutil.which(required_tool) is None:
            status = "failed" if strict_tools else "skipped"
            results.append(
                {
                    "id": fixture["id"],
                    "language": fixture["language"],
                    "status": status,
                    "critical": fixture["critical"],
                    "reason": f"required tool not found: {required_tool}",
                    "duration_ms": 0,
                }
            )
            continue
        if not candidate.exists():
            results.append(
                {
                    "id": fixture["id"],
                    "language": fixture["language"],
                    "status": "failed",
                    "critical": fixture["critical"],
                    "reason": f"candidate not found: {candidate}",
                    "duration_ms": 0,
                }
            )
            continue
        command = render_command(fixture["verify_command"], candidate)
        started = time.perf_counter()
        completed = subprocess.run(
            command,
            cwd=directory,
            capture_output=True,
            text=True,
            check=False,
            timeout=fixture.get("timeout_seconds", 60),
        )
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        results.append(
            {
                "id": fixture["id"],
                "language": fixture["language"],
                "status": "passed" if completed.returncode == 0 else "failed",
                "critical": fixture["critical"],
                "reason": completed.stderr.strip() or completed.stdout.strip() or None,
                "duration_ms": duration_ms,
            }
        )
    failed = [result for result in results if result["status"] == "failed"]
    critical_failed = [result for result in failed if result["critical"]]
    return {
        "schema_version": "1.0",
        "valid": not failed,
        "hard_gate_passed": not critical_failed,
        "counts": {
            "passed": sum(result["status"] == "passed" for result in results),
            "failed": len(failed),
            "skipped": sum(result["status"] == "skipped" for result in results),
        },
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path)
    parser.add_argument("--strict-tools", action="store_true")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    report = verify_fixtures(args.candidate_root, args.strict_tools)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered, encoding="utf-8", newline="\n")
    for result in report["results"]:
        print(f"{result['status'].upper():7} {result['id']} {result['language']}: {result['reason'] or 'ok'}")
    print(
        f"fixtures: passed={report['counts']['passed']} failed={report['counts']['failed']} "
        f"skipped={report['counts']['skipped']}"
    )
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
