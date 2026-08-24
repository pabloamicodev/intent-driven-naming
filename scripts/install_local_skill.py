#!/usr/bin/env python3
"""Install or verify the runtime-only skill payload at an explicit local destination."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import uuid
from collections.abc import Iterable
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

RUNTIME_DIRECTORY_SUFFIXES = {
    Path("agents"): frozenset({".yaml", ".yml"}),
    Path("references"): frozenset({".md"}),
    Path("scripts/runtime"): frozenset({".md", ".py"}),
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for relative in RUNTIME_PATHS:
        source = root / relative
        candidates: Iterable[Path]
        if source.is_dir():
            allowed_suffixes = RUNTIME_DIRECTORY_SUFFIXES[relative]
            candidates = (
                candidate
                for candidate in source.rglob("*")
                if candidate.suffix.lower() in allowed_suffixes
                and "__pycache__" not in candidate.parts
            )
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
    sources = runtime_files(ROOT)
    for relative, source in sorted(sources.items()):
        target = destination / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    manifest = {
        "schema_version": "2.0",
        "skill": "intent-driven-naming",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "files": {
            relative: file_hash(path)
            for relative, path in sorted(sources.items())
        },
    }
    (destination / "INSTALLATION.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def default_backup_directory(destination: Path) -> Path:
    """Keep replacements outside the one-level skill discovery surface."""
    if destination.parent.name.lower() == "skills":
        return destination.parent.parent / "skill-backups"
    return destination.parent / ".skill-backups"


def _next_backup_path(destination: Path, backup_directory: Path) -> Path:
    version = "unknown"
    version_path = destination / "VERSION"
    if version_path.is_file():
        version = version_path.read_text(encoding="utf-8").strip() or version
    base = backup_directory / f"{destination.name}-{version}"
    candidate = base
    suffix = 1
    while candidate.exists():
        candidate = backup_directory / f"{base.name}.{suffix}"
        suffix += 1
    return candidate


def _acquire_install_lock(destination: Path) -> Path:
    """Serialize concurrent installs targeting the same destination.

    Without this, two concurrent `--replace` runs can both pass the
    `_next_backup_path` check-then-act loop before either has moved anything,
    compute the same backup path, and then race each other's rename/rollback
    steps. An exclusive lock file makes the second run fail fast with a clear
    error instead of silently corrupting the first run's backup or payload.
    """
    lock_path = destination.parent / f".{destination.name}.install.lock"
    try:
        os.close(os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError as exc:
        raise ValueError(
            f"another install is already in progress for {destination} "
            f"(remove {lock_path} if a previous run crashed without cleaning up)"
        ) from exc
    return lock_path


def install(
    destination: Path,
    *,
    replace: bool = False,
    backup_directory: Path | None = None,
) -> Path | None:
    if destination.exists():
        if not replace:
            raise ValueError(
                f"destination already exists: {destination} (pass --replace to install over it)"
            )
        if not destination.is_dir():
            raise ValueError(f"destination is not a directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock_path = _acquire_install_lock(destination)
    try:
        staging = destination.with_name(f".{destination.name}.staging-{uuid.uuid4().hex}")
        backup: Path | None = None
        try:
            _write_installation(staging)
            if destination.exists():
                backup_directory = (
                    backup_directory or default_backup_directory(destination)
                ).resolve()
                if backup_directory.anchor.lower() != destination.anchor.lower():
                    raise ValueError("backup directory must be on the same filesystem anchor")
                try:
                    backup_directory.relative_to(destination.resolve())
                except ValueError:
                    pass
                else:
                    raise ValueError("backup directory cannot be inside the installed skill")
                if (
                    destination.parent.name.lower() == "skills"
                    and backup_directory == destination.parent.resolve()
                ):
                    raise ValueError(
                        "backup directory cannot be the one-level skill discovery directory"
                    )
                backup_directory.mkdir(parents=True, exist_ok=True)
                backup = _next_backup_path(destination, backup_directory)
                destination.replace(backup)
            staging.replace(destination)
        except Exception:
            if staging.exists():
                shutil.rmtree(staging)
            if backup is not None and backup.exists() and not destination.exists():
                backup.replace(destination)
            raise
        return backup
    finally:
        lock_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Atomically replace an existing installation and retain a versioned backup.",
    )
    parser.add_argument(
        "--backup-directory",
        type=Path,
        help="Replacement backup directory; defaults outside the skill discovery directory.",
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
        backup_directory = args.backup_directory.resolve() if args.backup_directory else None
        backup = install(destination, replace=args.replace, backup_directory=backup_directory)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"installed intent-driven-naming at {destination}")
    if backup is not None:
        print(f"previous installation retained at {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
