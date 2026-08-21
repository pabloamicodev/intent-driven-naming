#!/usr/bin/env python3
"""Install or verify the runtime-only skill payload at an explicit local destination."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATHS = (
    Path("SKILL.md"),
    Path("agents"),
    Path("references"),
    Path("scripts/runtime"),
    Path("specification/semantic-record.schema.json"),
    Path("specification/rename-plan.schema.json"),
    Path("LICENSE"),
    Path("VERSION"),
)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for relative in RUNTIME_PATHS:
        source = root / relative
        if source.is_dir():
            candidates = source.rglob("*")
        else:
            candidates = (source,)
        for candidate in candidates:
            if candidate.is_file():
                files[candidate.relative_to(root).as_posix()] = candidate
    return files


def verify_installation(destination: Path) -> list[str]:
    errors: list[str] = []
    expected = runtime_files(ROOT)
    actual = (
        {
            path.relative_to(destination).as_posix(): path
            for path in destination.rglob("*")
            if path.is_file() and path.name != "INSTALLATION.json"
        }
        if destination.is_dir()
        else {}
    )
    for relative, source in expected.items():
        installed = actual.get(relative)
        if installed is None:
            errors.append(f"missing installed file: {relative}")
        elif file_hash(source) != file_hash(installed):
            errors.append(f"installed file differs: {relative}")
    unexpected = sorted(set(actual) - set(expected))
    errors.extend(f"unexpected runtime file: {relative}" for relative in unexpected)
    manifest_path = destination / "INSTALLATION.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid installation manifest: {exc}")
    else:
        expected_hashes = {
            relative: file_hash(path) for relative, path in sorted(expected.items())
        }
        if manifest.get("skill") != "intent-driven-naming":
            errors.append("installation manifest has the wrong skill name")
        if manifest.get("files") != expected_hashes:
            errors.append("installation manifest hashes do not match source")
    return errors


def _write_installation(destination: Path) -> None:
    destination.mkdir(parents=True)
    for relative in RUNTIME_PATHS:
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
    manifest = {
        "schema_version": "2.0",
        "skill": "intent-driven-naming",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "files": {
            relative: file_hash(path)
            for relative, path in sorted(runtime_files(ROOT).items())
        },
    }
    (destination / "INSTALLATION.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _next_backup_path(destination: Path) -> Path:
    version = "unknown"
    version_path = destination / "VERSION"
    if version_path.is_file():
        version = version_path.read_text(encoding="utf-8").strip() or version
    base = destination.with_name(f"{destination.name}.backup-{version}")
    candidate = base
    suffix = 1
    while candidate.exists():
        candidate = destination.with_name(f"{base.name}.{suffix}")
        suffix += 1
    return candidate


def install(destination: Path, *, replace: bool = False) -> Path | None:
    if destination.exists():
        if not replace:
            raise ValueError(f"destination already exists: {destination}")
        if not destination.is_dir():
            raise ValueError(f"destination is not a directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(f".{destination.name}.staging-{uuid.uuid4().hex}")
    backup: Path | None = None
    try:
        _write_installation(staging)
        if destination.exists():
            backup = _next_backup_path(destination)
            destination.replace(backup)
        staging.replace(destination)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        if backup is not None and backup.exists() and not destination.exists():
            backup.replace(destination)
        raise
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Atomically replace an existing installation and retain a versioned backup.",
    )
    args = parser.parse_args()
    destination = args.destination.resolve()
    try:
        if args.check:
            errors = verify_installation(destination)
            if errors:
                print("\n".join(errors), file=sys.stderr)
                return 1
            print(f"installed runtime matches source: {destination}")
            return 0
        backup = install(destination, replace=args.replace)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"installed intent-driven-naming at {destination}")
    if backup is not None:
        print(f"previous installation retained at {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
