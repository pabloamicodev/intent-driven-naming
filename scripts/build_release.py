#!/usr/bin/env python3
"""Build a deterministic runtime archive, checksum manifest, and SPDX file inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
import zipfile
from pathlib import Path

try:
    from scripts.install_local_skill import ROOT, runtime_files
except ModuleNotFoundError:  # Direct execution puts scripts/ first on sys.path.
    from install_local_skill import ROOT, runtime_files  # type: ignore[no-redef, import-not-found]


ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _package_manifest(version: str, entries: dict[str, bytes]) -> bytes:
    document = {
        "schema_version": "1.0",
        "skill": "intent-driven-naming",
        "version": version,
        "files": {
            relative: _digest(content) for relative, content in sorted(entries.items())
        },
    }
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build(output_directory: Path) -> dict[str, Path]:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    output_directory.mkdir(parents=True, exist_ok=True)
    archive = output_directory / f"intent-driven-naming-{version}.zip"
    checksums = output_directory / "SHA256SUMS"
    sbom = output_directory / f"intent-driven-naming-{version}.spdx.json"
    source_files = runtime_files(ROOT)
    entries = {
        relative: source.read_bytes() for relative, source in sorted(source_files.items())
    }
    entries["PACKAGE-MANIFEST.json"] = _package_manifest(version, entries)

    # Build every artifact under a staging name first and only rename into the
    # published path once everything is complete, so a concurrent reader (or a
    # build interrupted partway through) never observes a truncated zip or a
    # SHA256SUMS that doesn't yet match what's on disk.
    token = uuid.uuid4().hex
    staged_archive = archive.with_name(f"{archive.name}.staging-{token}")
    staged_sbom = sbom.with_name(f"{sbom.name}.staging-{token}")
    staged_checksums = checksums.with_name(f"{checksums.name}.staging-{token}")
    try:
        _build_staged_artifacts(
            version, entries, staged_archive=staged_archive, staged_sbom=staged_sbom
        )
        checksum_entries = sorted(
            [(archive.name, _sha256(staged_archive)), (sbom.name, _sha256(staged_sbom))]
        )
        staged_checksums.write_text(
            "".join(f"{digest}  {name}\n" for name, digest in checksum_entries),
            encoding="utf-8",
            newline="\n",
        )
        staged_archive.replace(archive)
        staged_sbom.replace(sbom)
        staged_checksums.replace(checksums)
    finally:
        for staged in (staged_archive, staged_sbom, staged_checksums):
            staged.unlink(missing_ok=True)
    return {"archive": archive, "checksums": checksums, "sbom": sbom}


def _build_staged_artifacts(
    version: str, entries: dict[str, bytes], *, staged_archive: Path, staged_sbom: Path
) -> None:
    with zipfile.ZipFile(
        staged_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as bundle:
        for relative, content in sorted(entries.items()):
            info = zipfile.ZipInfo(f"intent-driven-naming/{relative}", ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            bundle.writestr(info, content, compresslevel=9)
    document_namespace = f"https://github.com/pabloamicodev/intent-driven-naming/releases/tag/v{version}"
    sbom_document = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"intent-driven-naming-{version}",
        "documentNamespace": document_namespace,
        "creationInfo": {"creators": ["Tool: scripts/build_release.py"], "created": "1980-01-01T00:00:00Z"},
        "packages": [{
            "name": "intent-driven-naming",
            "SPDXID": "SPDXRef-Package",
            "versionInfo": version,
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": True,
            "licenseConcluded": "Apache-2.0",
            "licenseDeclared": "Apache-2.0",
        }],
        "files": [
            {
                "fileName": relative,
                "SPDXID": f"SPDXRef-File-{index:04d}",
                "checksums": [{"algorithm": "SHA256", "checksumValue": _digest(content)}],
                "licenseConcluded": "Apache-2.0",
            }
            for index, (relative, content) in enumerate(sorted(entries.items()), start=1)
        ],
        "relationships": [
            {"spdxElementId": "SPDXRef-Package", "relationshipType": "CONTAINS", "relatedSpdxElement": f"SPDXRef-File-{index:04d}"}
            for index in range(1, len(entries) + 1)
        ],
    }
    staged_sbom.write_text(
        json.dumps(sbom_document, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.clean and output.exists():
        shutil.rmtree(output)
    artifacts = build(output)
    for label, path in artifacts.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
