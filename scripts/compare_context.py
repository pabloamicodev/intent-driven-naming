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

ROOT = Path(__file__).resolve().parents[1]


def _words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _git_content(revision: str, relative: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(detail or f"cannot read {revision}:{relative}")
    return completed.stdout


def _measure(read_content: Callable[[str], bytes]) -> dict[str, object]:
    def decoded(relative: str) -> str:
        return read_content(relative).decode("utf-8")

    routes = json.loads(decoded("specification/routes.json"))
    all_paths = set(routes["always"])
    for group_name in ("conditional_core", "modes", "features", "profiles"):
        for paths in routes[group_name].values():
            all_paths.update(paths)
    contents = {path: read_content(path) for path in sorted(all_paths)}
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


def compare(baseline_ref: str) -> dict[str, object]:
    current = _measure(lambda relative: (ROOT / relative).read_bytes())
    baseline = _measure(lambda relative: _git_content(baseline_ref, relative))
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
