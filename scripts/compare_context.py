#!/usr/bin/env python3
"""Compare composed context routes with a frozen Git revision."""

from __future__ import annotations

import argparse
import itertools
import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
SKILL_PREFIX = "skills/intent-driven-naming/"


def _resolve(relative: str) -> str:
    """Map a routes.json path (skill-relative) to a repo-relative path.

    specification/*.json stays at the repo root; everything else (SKILL.md,
    references/*.md) now lives under skills/intent-driven-naming/.
    """
    return relative if relative.startswith("specification/") else f"{SKILL_PREFIX}{relative}"


class _RouteWordLabel(TypedDict):
    name: str
    words: int


class _RouteByteLabel(TypedDict):
    name: str
    bytes: int


class RouteMeasurement(TypedDict):
    entrypoint_words: int
    entrypoint_bytes: int
    always_loaded_words: int
    always_loaded_bytes: int
    runtime_instruction_words: int
    runtime_instruction_bytes: int
    maximum_standard_route: _RouteWordLabel
    maximum_standard_byte_route: _RouteByteLabel
    maximum_extended_route: _RouteWordLabel
    maximum_extended_byte_route: _RouteByteLabel


class ComparisonReductions(TypedDict):
    entrypoint: float
    always_loaded: float
    runtime_instructions: float
    maximum_standard_route: float
    maximum_extended_route: float
    entrypoint_bytes: float
    always_loaded_bytes: float
    runtime_instruction_bytes: float
    maximum_standard_route_bytes: float
    maximum_extended_route_bytes: float


class ComparisonReport(TypedDict):
    schema_version: str
    measurement: str
    byte_measurement: str
    baseline_ref: str
    current: RouteMeasurement
    baseline: RouteMeasurement
    reductions: ComparisonReductions


def _words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _git_content_batch(revision: str, relatives: list[str]) -> dict[str, bytes]:
    """Read many blobs from one revision with a single `git cat-file --batch` call.

    Spawning one `git show` subprocess per routed file is correct but costly
    (process-spawn overhead, especially on Windows) once the route table has
    dozens of entries; `--batch` resolves and streams every blob over one
    pipe instead.
    """
    if not relatives:
        return {}
    requests = [f"{revision}:{relative}" for relative in relatives]
    completed = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        input=("\n".join(requests) + "\n").encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(detail or f"cannot read batch content at {revision}")
    contents: dict[str, bytes] = {}
    stream = completed.stdout
    offset = 0
    for relative in relatives:
        newline = stream.index(b"\n", offset)
        header = stream[offset:newline].decode("utf-8", errors="replace")
        offset = newline + 1
        if header.endswith(" missing"):
            raise ValueError(f"cannot read {revision}:{relative}: not found")
        size = int(header.rsplit(" ", 2)[-1])
        contents[relative] = stream[offset : offset + size]
        offset += size + 1  # skip the blob's trailing newline
    return contents


def _measure(read_many: Callable[[list[str]], dict[str, bytes]]) -> RouteMeasurement:
    def decoded(relative: str) -> str:
        resolved = _resolve(relative)
        return read_many([resolved])[resolved].decode("utf-8")

    routes = json.loads(decoded("specification/routes.json"))
    all_paths = set(routes["always"])
    for group_name in ("conditional_core", "modes", "features", "profiles"):
        for paths in routes[group_name].values():
            all_paths.update(paths)
    # Keep counts/byte_counts keyed by the logical (skill-relative) route path
    # even though the actual bytes are fetched from the resolved repo-relative
    # location, so every downstream label/budget lookup stays unchanged.
    resolved_by_path = {path: _resolve(path) for path in all_paths}
    raw_contents = read_many(sorted(set(resolved_by_path.values())))
    contents = {path: raw_contents[resolved] for path, resolved in resolved_by_path.items()}
    counts = {path: _words(content.decode("utf-8")) for path, content in contents.items()}
    byte_counts = {path: len(content) for path, content in contents.items()}
    modes = list(routes["modes"].items())
    features = list(routes["features"].items())
    profiles = list(routes["profiles"].items())
    feature_choices = [()] + [(feature,) for feature in features] + [tuple(features)]
    standard: list[tuple[str, int]] = []
    standard_bytes: list[tuple[str, int]] = []
    for (mode_name, mode_paths), feature_choice, (profile_name, profile_paths) in itertools.product(
        modes, feature_choices, profiles
    ):
        paths = [*routes["always"], *mode_paths, *profile_paths]
        names = []
        for feature_name, feature_paths in feature_choice:
            names.append(feature_name)
            paths.extend(feature_paths)
        label = f"{mode_name}+{'+'.join(names) if names else 'no-feature'}+{profile_name}"
        unique_paths = list(dict.fromkeys(paths))
        standard.append((label, sum(counts[path] for path in unique_paths)))
        standard_bytes.append((label, sum(byte_counts[path] for path in unique_paths)))
    maximum_profiles = json.loads(decoded("specification/context-budgets.json")).get(
        "maximum_simultaneous_profiles", 1
    )
    conditional = [path for paths in routes["conditional_core"].values() for path in paths]
    extended: list[tuple[str, int]] = []
    extended_bytes: list[tuple[str, int]] = []
    for (mode_name, mode_paths), feature_choice in itertools.product(modes, feature_choices):
        for profile_count in range(1, min(maximum_profiles, len(profiles)) + 1):
            for profile_choice in itertools.combinations(profiles, profile_count):
                paths = [*routes["always"], *mode_paths, *conditional]
                feature_names = []
                for feature_name, feature_paths in feature_choice:
                    feature_names.append(feature_name)
                    paths.extend(feature_paths)
                profile_names = []
                for profile_name, profile_paths in profile_choice:
                    profile_names.append(profile_name)
                    paths.extend(profile_paths)
                label = (
                    f"{mode_name}+{'+'.join(feature_names) if feature_names else 'no-feature'}+"
                    f"{'+'.join(profile_names)}"
                )
                unique_paths = list(dict.fromkeys(paths))
                extended.append((label, sum(counts[path] for path in unique_paths)))
                extended_bytes.append((label, sum(byte_counts[path] for path in unique_paths)))
    max_standard = max(standard, key=lambda item: item[1])
    max_standard_bytes = max(standard_bytes, key=lambda item: item[1])
    max_extended = max(extended, key=lambda item: item[1])
    max_extended_bytes = max(extended_bytes, key=lambda item: item[1])
    return {
        "entrypoint_words": counts["SKILL.md"],
        "entrypoint_bytes": byte_counts["SKILL.md"],
        "always_loaded_words": sum(counts[path] for path in dict.fromkeys(routes["always"])),
        "always_loaded_bytes": sum(byte_counts[path] for path in dict.fromkeys(routes["always"])),
        "runtime_instruction_words": sum(
            count
            for path, count in counts.items()
            if path == "SKILL.md" or path.startswith("references/")
        ),
        "runtime_instruction_bytes": sum(
            count
            for path, count in byte_counts.items()
            if path == "SKILL.md" or path.startswith("references/")
        ),
        "maximum_standard_route": {"name": max_standard[0], "words": max_standard[1]},
        "maximum_standard_byte_route": {
            "name": max_standard_bytes[0],
            "bytes": max_standard_bytes[1],
        },
        "maximum_extended_route": {"name": max_extended[0], "words": max_extended[1]},
        "maximum_extended_byte_route": {
            "name": max_extended_bytes[0],
            "bytes": max_extended_bytes[1],
        },
    }


def _reduction(current: int, baseline: int) -> float:
    return round(1 - current / baseline, 6)


def compare(baseline_ref: str) -> ComparisonReport:
    current = _measure(
        lambda relatives: {relative: (ROOT / relative).read_bytes() for relative in relatives}
    )
    baseline = _measure(lambda relatives: _git_content_batch(baseline_ref, relatives))
    return {
        "schema_version": "2.0",
        "measurement": "whitespace-delimited words",
        "byte_measurement": "UTF-8 source bytes",
        "baseline_ref": baseline_ref,
        "current": current,
        "baseline": baseline,
        "reductions": {
            "entrypoint": _reduction(current["entrypoint_words"], baseline["entrypoint_words"]),
            "always_loaded": _reduction(
                current["always_loaded_words"], baseline["always_loaded_words"]
            ),
            "runtime_instructions": _reduction(
                current["runtime_instruction_words"], baseline["runtime_instruction_words"]
            ),
            "maximum_standard_route": _reduction(
                current["maximum_standard_route"]["words"],
                baseline["maximum_standard_route"]["words"],
            ),
            "maximum_extended_route": _reduction(
                current["maximum_extended_route"]["words"],
                baseline["maximum_extended_route"]["words"],
            ),
            "entrypoint_bytes": _reduction(
                current["entrypoint_bytes"], baseline["entrypoint_bytes"]
            ),
            "always_loaded_bytes": _reduction(
                current["always_loaded_bytes"], baseline["always_loaded_bytes"]
            ),
            "runtime_instruction_bytes": _reduction(
                current["runtime_instruction_bytes"], baseline["runtime_instruction_bytes"]
            ),
            "maximum_standard_route_bytes": _reduction(
                current["maximum_standard_byte_route"]["bytes"],
                baseline["maximum_standard_byte_route"]["bytes"],
            ),
            "maximum_extended_route_bytes": _reduction(
                current["maximum_extended_byte_route"]["bytes"],
                baseline["maximum_extended_byte_route"]["bytes"],
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", required=True)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    try:
        report = compare(args.baseline_ref)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
