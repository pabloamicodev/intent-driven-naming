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


def _git_text(revision: str, relative: str) -> str:
    completed = subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or f"cannot read {revision}:{relative}")
    return completed.stdout


def _measure(read_text: Callable[[str], str]) -> dict[str, object]:
    routes = json.loads(read_text("specification/routes.json"))
    all_paths = set(routes["always"])
    for group_name in ("conditional_core", "modes", "features", "profiles"):
        for paths in routes[group_name].values():
            all_paths.update(paths)
    counts = {path: _words(read_text(path)) for path in sorted(all_paths)}
    modes = list(routes["modes"].items())
    features = list(routes["features"].items())
    profiles = list(routes["profiles"].items())
    feature_choices = [()] + [(feature,) for feature in features] + [tuple(features)]
    standard: list[tuple[str, int]] = []
    for (mode_name, mode_paths), feature_choice, (profile_name, profile_paths) in itertools.product(
        modes, feature_choices, profiles
    ):
        paths = [*routes["always"], *mode_paths, *profile_paths]
        names = []
        for feature_name, feature_paths in feature_choice:
            names.append(feature_name)
            paths.extend(feature_paths)
        standard.append(
            (
                f"{mode_name}+{'+'.join(names) if names else 'no-feature'}+{profile_name}",
                sum(counts[path] for path in dict.fromkeys(paths)),
            )
        )
    maximum_profiles = json.loads(read_text("specification/context-budgets.json")).get(
        "maximum_simultaneous_profiles", 1
    )
    conditional = [
        path for paths in routes["conditional_core"].values() for path in paths
    ]
    extended: list[tuple[str, int]] = []
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
                extended.append(
                    (
                        f"{mode_name}+{'+'.join(feature_names) if feature_names else 'no-feature'}+{'+'.join(profile_names)}",
                        sum(counts[path] for path in dict.fromkeys(paths)),
                    )
                )
    max_standard = max(standard, key=lambda item: item[1])
    max_extended = max(extended, key=lambda item: item[1])
    return {
        "entrypoint_words": counts["SKILL.md"],
        "always_loaded_words": sum(counts[path] for path in dict.fromkeys(routes["always"])),
        "runtime_instruction_words": sum(
            count for path, count in counts.items() if path == "SKILL.md" or path.startswith("references/")
        ),
        "maximum_standard_route": {"name": max_standard[0], "words": max_standard[1]},
        "maximum_extended_route": {"name": max_extended[0], "words": max_extended[1]},
    }


def _reduction(current: int, baseline: int) -> float:
    return round(1 - current / baseline, 6)


def compare(baseline_ref: str) -> dict[str, object]:
    current = _measure(lambda relative: (ROOT / relative).read_text(encoding="utf-8"))
    baseline = _measure(lambda relative: _git_text(baseline_ref, relative))
    return {
        "schema_version": "1.0",
        "measurement": "whitespace-delimited words",
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
