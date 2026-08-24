#!/usr/bin/env python3
"""Create a deterministic, reviewable JSON bundle from explicitly included text artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, NotRequired, TypedDict

SENSITIVE_NAME = re.compile(
    r"(^|[._-])(\.env|credentials?|secrets?|tokens?|id_rsa)([._-]|$)|\.(pem|key|p12|pfx)$",
    re.IGNORECASE,
)
SENSITIVE_CONTENT = (
    ("private key", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b")),
    ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
)


class BundleFile(TypedDict):
    path: str
    sha256: str
    content: str


class ArtifactBundleContent(TypedDict):
    schema_version: str
    root_label: str
    total_bytes: int
    files: list[BundleFile]
    verifier_report: NotRequired[dict[str, Any]]


def _resolve_inside(root: Path, relative: str) -> Path:
    unresolved = root / relative
    if unresolved.is_symlink():
        raise ValueError(f"symlinks are not allowed: {relative}")
    candidate = unresolved.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes artifact root: {relative}") from exc
    return candidate


def build_bundle(root: Path, includes: list[str], max_bytes: int) -> ArtifactBundleContent:
    root = root.resolve()
    selected: set[Path] = set()
    for relative in includes:
        target = _resolve_inside(root, relative)
        if not target.exists():
            raise ValueError(f"included path does not exist: {relative}")
        candidates = target.rglob("*") if target.is_dir() else (target,)
        for candidate in candidates:
            if candidate.is_dir():
                continue
            if candidate.is_symlink():
                raise ValueError(f"symlinks are not allowed: {candidate.relative_to(root)}")
            selected.add(candidate)
    files: list[BundleFile] = []
    total_bytes = 0
    for path in sorted(selected, key=lambda value: value.as_posix()):
        relative = path.relative_to(root).as_posix()
        if any(SENSITIVE_NAME.search(part) for part in Path(relative).parts):
            raise ValueError(f"sensitive-looking artifact requires manual exclusion: {relative}")
        content_bytes = path.read_bytes()
        total_bytes += len(content_bytes)
        if total_bytes > max_bytes:
            raise ValueError(f"artifact content exceeds {max_bytes} bytes")
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"binary or non-UTF-8 artifact is not allowed: {relative}") from exc
        for secret_type, pattern in SENSITIVE_CONTENT:
            if pattern.search(content):
                raise ValueError(
                    f"{secret_type} detected in artifact content; exclude or redact {relative}"
                )
        files.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(content_bytes).hexdigest(),
                "content": content,
            }
        )
    if not files:
        raise ValueError("artifact bundle must contain at least one file")
    return {
        "schema_version": "1.0",
        "root_label": root.name,
        "total_bytes": total_bytes,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--include", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verifier-report", type=Path)
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    args = parser.parse_args()
    if args.max_bytes < 1:
        parser.error("--max-bytes must be positive")
    try:
        bundle = build_bundle(args.root, args.include, args.max_bytes)
        if args.verifier_report:
            verifier_path = args.verifier_report.resolve()
            root = args.root.resolve()
            try:
                verifier_path.relative_to(root)
            except ValueError as exc:
                raise ValueError("verifier report must be inside --root") from exc
            verifier = json.loads(verifier_path.read_text(encoding="utf-8"))
            if not isinstance(verifier, dict):
                raise ValueError("verifier report must be a JSON object")
            bundle["verifier_report"] = verifier
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    rendered = json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote artifact bundle {args.output} sha256={hashlib.sha256(rendered.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
