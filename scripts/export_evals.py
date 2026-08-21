#!/usr/bin/env python3
"""Export human-readable evaluation cases to stable JSONL datasets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRIGGER_SOURCE = ROOT / "evals" / "trigger-cases.md"
BEHAVIOR_SOURCE = ROOT / "evals" / "behavior-cases.md"
OUTPUT_DIR = ROOT / "evals" / "cases"
ACTIVATION_OUTPUT = OUTPUT_DIR / "activation.jsonl"
BEHAVIOR_OUTPUT = OUTPUT_DIR / "behavior.jsonl"

TRIGGER_ROW = re.compile(
    r"^\| (T\d{2}) \| (.*?) \| (Trigger|Do not trigger) \| (.*?) \|$"
)
BEHAVIOR_HEADING = re.compile(r"^## (B\d{2}) — (.+)$")


def normalize_inline_markdown(value: str) -> str:
    return value.replace("`", "").strip()


def derive_tags(text: str, base: list[str]) -> list[str]:
    lowered = text.lower()
    keyword_tags = {
        "typescript": "typescript",
        "javascript": "javascript",
        "react": "react",
        "python": "python",
        "ruby": "ruby",
        "php": "php",
        " go ": "go",
        "rust": "rust",
        "c++": "cpp",
        "java ": "java",
        "kotlin": "kotlin",
        "c#": "csharp",
        "swift": "swift",
        "dart": "dart",
        "elixir": "elixir",
        "sql": "sql",
        "terraform": "terraform",
        "powershell": "powershell",
        "schema": "schema",
        "public api": "public-api",
        "external": "contract",
        "serialized": "serialization",
        "json": "serialization",
        "unit": "unit",
        "boolean": "boolean",
        "function": "callable",
        "method": "callable",
        "local": "local-variable",
        "accumulator": "local-variable",
        "audit": "audit",
        "review": "audit",
        "refactor": "refactor",
        "implement": "generation",
        "create": "generation",
        "no-op": "no-op",
    }
    tags = list(base)
    padded = f" {lowered} "
    for keyword, tag in keyword_tags.items():
        haystack = padded if keyword.startswith(" ") or keyword.endswith(" ") else lowered
        if keyword in haystack and tag not in tags:
            tags.append(tag)
    return tags


def parse_activation_cases(markdown: str) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for line in markdown.splitlines():
        match = TRIGGER_ROW.match(line)
        if not match:
            continue
        case_id, prompt, expectation, rationale = match.groups()
        expected = expectation == "Trigger"
        clean_prompt = normalize_inline_markdown(prompt)
        clean_rationale = normalize_inline_markdown(rationale)
        tags = derive_tags(
            f"{clean_prompt} {clean_rationale}",
            ["activation", "positive" if expected else "negative"],
        )
        cases.append(
            {
                "schema_version": "1.0",
                "id": case_id,
                "suite": "activation",
                "title": f"Activation {case_id}",
                "prompt": clean_prompt,
                "tags": tags,
                "expected_activation": expected,
                "rationale": clean_rationale,
            }
        )
    return cases


def extract_fenced_block(lines: list[str], start: int) -> tuple[str, int]:
    index = start
    while index < len(lines) and not lines[index].startswith("```"):
        index += 1
    if index >= len(lines):
        raise ValueError("Expected fenced prompt block")
    index += 1
    content: list[str] = []
    while index < len(lines) and not lines[index].startswith("```"):
        content.append(lines[index])
        index += 1
    if index >= len(lines):
        raise ValueError("Unterminated fenced prompt block")
    return "\n".join(content).strip(), index + 1


def invariant_metadata(description: str) -> tuple[str, str]:
    lowered = description.lower()
    critical_markers = (
        "behavior",
        "contract",
        "serialized",
        "external",
        "public",
        "runtime",
        "not changed",
        "unchanged",
        "does not edit",
        "no files are modified",
        "preserved",
        "remains unchanged",
        "does not replace",
    )
    deterministic_markers = (
        "no files are modified",
        "numeric value",
        "serialized output",
        "field remains",
        "spelling remains",
        "loop structure",
        "message tag",
        "stored column",
        "resource label",
        "output shape",
    )
    severity = "critical" if any(marker in lowered for marker in critical_markers) else "major"
    grading = "deterministic" if any(marker in lowered for marker in deterministic_markers) else "semantic"
    return severity, grading


def parse_behavior_cases(markdown: str) -> list[dict[str, object]]:
    lines = markdown.splitlines()
    cases: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        heading = BEHAVIOR_HEADING.match(lines[index])
        if not heading:
            index += 1
            continue
        case_id, title = heading.groups()
        section_end = index + 1
        while section_end < len(lines) and not BEHAVIOR_HEADING.match(lines[section_end]):
            if lines[section_end] == "## Scoring":
                break
            section_end += 1
        section = lines[index:section_end]
        try:
            prompt_heading = section.index("### Prompt")
            prompt, _ = extract_fenced_block(section, prompt_heading + 1)
            invariants_heading = section.index("### Required invariants")
        except ValueError as exc:
            raise ValueError(f"Malformed behavior case {case_id}: {exc}") from exc
        invariant_lines: list[str] = []
        for line in section[invariants_heading + 1 :]:
            if line.startswith("### "):
                break
            if line.startswith("- "):
                invariant_lines.append(line[2:].strip())
        if not invariant_lines:
            raise ValueError(f"Behavior case {case_id} has no required invariants")
        invariants: list[dict[str, str]] = []
        for invariant_index, description in enumerate(invariant_lines, start=1):
            severity, grading = invariant_metadata(description)
            invariants.append(
                {
                    "id": f"{case_id.lower()}-{invariant_index:02d}",
                    "description": description,
                    "severity": severity,
                    "grading": grading,
                }
            )
        tags = derive_tags(f"{title} {prompt}", ["behavior"])
        cases.append(
            {
                "schema_version": "1.0",
                "id": case_id,
                "suite": "behavior",
                "title": title,
                "prompt": prompt,
                "tags": tags,
                "invariants": invariants,
            }
        )
        index = section_end
    return cases


def serialize_jsonl(records: list[dict[str, object]]) -> str:
    return "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)


def build_outputs() -> dict[Path, str]:
    activation_cases = parse_activation_cases(TRIGGER_SOURCE.read_text(encoding="utf-8"))
    behavior_cases = parse_behavior_cases(BEHAVIOR_SOURCE.read_text(encoding="utf-8"))
    if len(activation_cases) != 36:
        raise ValueError(f"Expected 36 activation cases, found {len(activation_cases)}")
    if len(behavior_cases) != 34:
        raise ValueError(f"Expected 34 behavior cases, found {len(behavior_cases)}")
    return {
        ACTIVATION_OUTPUT: serialize_jsonl(activation_cases),
        BEHAVIOR_OUTPUT: serialize_jsonl(behavior_cases),
    }


def write_outputs(outputs: dict[Path, str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(ROOT)}")


def check_outputs(outputs: dict[Path, str]) -> int:
    stale: list[str] = []
    for path, expected in outputs.items():
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            stale.append(str(path.relative_to(ROOT)))
    if stale:
        print("Generated evaluation datasets are stale:", file=sys.stderr)
        for path in stale:
            print(f"- {path}", file=sys.stderr)
        print("Run: python scripts/export_evals.py --write", file=sys.stderr)
        return 1
    print("evaluation datasets are current")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write generated JSONL datasets")
    mode.add_argument("--check", action="store_true", help="fail if generated datasets are stale")
    args = parser.parse_args()

    outputs = build_outputs()
    if args.write:
        write_outputs(outputs)
        return 0
    return check_outputs(outputs)


if __name__ == "__main__":
    raise SystemExit(main())
