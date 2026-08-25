#!/usr/bin/env python3
"""Build the OpenAI plugin submission archive (skills-only, .codex-plugin manifest)."""

from __future__ import annotations

import argparse
import json
import uuid
import zipfile
from pathlib import Path

try:
    from scripts.install_local_skill import ROOT, SKILL_ROOT, installed_runtime_files
except ModuleNotFoundError:  # Direct execution puts scripts/ first on sys.path.
    from install_local_skill import (  # type: ignore[no-redef, import-not-found]
        ROOT,
        SKILL_ROOT,
        installed_runtime_files,
    )

ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
SKILL_NAME = "intent-driven-naming"


def _plugin_manifest(version: str) -> bytes:
    document = {
        "name": SKILL_NAME,
        "version": version,
        "description": (
            "A portable Agent Skill that helps AI coding agents design, audit, and "
            "safely refactor software identifiers across languages while preserving "
            "behavior and contracts."
        ),
        "author": {
            "name": "pabloamicodev",
            "url": "https://github.com/pabloamicodev/intent-driven-naming",
        },
        "homepage": "https://github.com/pabloamicodev/intent-driven-naming",
        "repository": "https://github.com/pabloamicodev/intent-driven-naming",
        "license": "Apache-2.0",
        "keywords": ["naming", "refactoring", "code-quality", "identifiers", "clean-code"],
        "skills": "./skills/",
    }
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write(bundle: zipfile.ZipFile, arcname: str, content: bytes) -> None:
    info = zipfile.ZipInfo(arcname, ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o100644 & 0xFFFF) << 16
    bundle.writestr(info, content, compresslevel=9)


def build(output_directory: Path) -> Path:
    version = (SKILL_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    output_directory.mkdir(parents=True, exist_ok=True)
    archive = output_directory / f"{SKILL_NAME}-openai-plugin-{version}.zip"
    skill_sources = installed_runtime_files()
    manifest_bytes = _plugin_manifest(version)
    openai_yaml = (SKILL_ROOT / "agents" / "openai.yaml").read_bytes()

    # Stage under a temporary name so a concurrent reader never observes a
    # truncated archive.
    token = uuid.uuid4().hex
    staged_archive = archive.with_name(f"{archive.name}.staging-{token}")
    try:
        with zipfile.ZipFile(
            staged_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as bundle:
            _write(bundle, ".codex-plugin/plugin.json", manifest_bytes)
            _write(bundle, "agents/openai.yaml", openai_yaml)
            for relative, source in sorted(skill_sources.items()):
                _write(bundle, f"skills/{SKILL_NAME}/{relative}", source.read_bytes())
        staged_archive.replace(archive)
    finally:
        staged_archive.unlink(missing_ok=True)
    return archive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    archive = build(args.output.resolve())
    print(f"archive: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
