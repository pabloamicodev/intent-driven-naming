#!/usr/bin/env python3
"""Export explicit human-reviewed evaluation metadata to stable JSONL and a manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRIGGER_SOURCE = ROOT / "evals" / "trigger-cases.md"
BEHAVIOR_SOURCE = ROOT / "evals" / "behavior-cases.md"
DATASET_VERSION_PATH = ROOT / "evals" / "DATASET_VERSION"
OUTPUT_DIR = ROOT / "evals" / "cases"
ACTIVATION_OUTPUT = OUTPUT_DIR / "activation.jsonl"
BEHAVIOR_OUTPUT = OUTPUT_DIR / "behavior.jsonl"
MANIFEST_OUTPUT = ROOT / "evals" / "manifest.json"

TRIGGER_ROW = re.compile(
    r"^\| (T\d{2}) \| (.*?) \| (Trigger|Do not trigger) \| "
    r"(easy|standard|edge|adversarial) \| ([a-z]{2}(?:-[A-Z]{2})?) \| (.*?) \|$"
)
BEHAVIOR_HEADING = re.compile(r"^## (B\d{2}) — (.+)$")
INVARIANT_ROW = re.compile(
    r"^- \[(critical|major|minor)\]\[(deterministic|semantic|human)\] (.+)$"
)
VALID_MODES = {"generation", "audit", "refactor"}
VALID_DIFFICULTIES = {"easy", "standard", "edge", "adversarial"}
VALID_RISKS = {
    "internal", "cross-module", "external", "dynamic", "generated", "stateful", "unknown"
}
VALID_DECISIONS = {"keep", "rename", "map", "migrate", "defer", "not-applicable"}


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


def dataset_version() -> str:
    version = DATASET_VERSION_PATH.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Invalid evals/DATASET_VERSION: {version}")
    return version


def parse_activation_cases(markdown: str, version: str | None = None) -> list[dict[str, Any]]:
    version = version or dataset_version()
    cases: list[dict[str, Any]] = []
    for line in markdown.splitlines():
        match = TRIGGER_ROW.match(line)
        if not match:
            continue
        case_id, prompt, expectation, difficulty, locale, rationale = match.groups()
        expected = expectation == "Trigger"
        clean_prompt = normalize_inline_markdown(prompt)
        clean_rationale = normalize_inline_markdown(rationale)
        tags = derive_tags(
            f"{clean_prompt} {clean_rationale}",
            [
                "activation",
                "positive" if expected else "negative",
                difficulty,
                f"locale-{locale.lower()}",
            ],
        )
        cases.append(
            {
                "schema_version": "1.0",
                "dataset_version": version,
                "id": case_id,
                "suite": "activation",
                "title": f"Activation {case_id}",
                "prompt": clean_prompt,
                "tags": tags,
                "difficulty": difficulty,
                "locale": locale,
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


def parse_metadata(section: list[str], case_id: str) -> dict[str, Any]:
    try:
        metadata_heading = section.index("### Case metadata")
        prompt_heading = section.index("### Prompt")
    except ValueError as exc:
        raise ValueError(f"{case_id}: missing case metadata or prompt heading") from exc
    values: dict[str, str] = {}
    for line in section[metadata_heading + 1 : prompt_heading]:
        match = re.match(r"^- ([A-Za-z ]+): (.+)$", line)
        if match:
            values[match.group(1).lower().replace(" ", "_")] = match.group(2).strip()
    required = {
        "mode",
        "difficulty",
        "locale",
        "languages",
        "contract_risk",
        "expected_decisions",
    }
    missing = required - set(values)
    if missing:
        raise ValueError(f"{case_id}: missing metadata {sorted(missing)}")
    languages = [value.strip() for value in values["languages"].split(",")]
    decisions = [value.strip() for value in values["expected_decisions"].split(",")]
    if values["mode"] not in VALID_MODES:
        raise ValueError(f"{case_id}: invalid mode {values['mode']}")
    if values["difficulty"] not in VALID_DIFFICULTIES:
        raise ValueError(f"{case_id}: invalid difficulty {values['difficulty']}")
    if values["contract_risk"] not in VALID_RISKS:
        raise ValueError(f"{case_id}: invalid contract risk {values['contract_risk']}")
    if not languages or any(not value for value in languages):
        raise ValueError(f"{case_id}: languages must be non-empty")
    if not decisions or any(value not in VALID_DECISIONS for value in decisions):
        raise ValueError(f"{case_id}: invalid expected decisions {decisions}")
    return {
        "mode": values["mode"],
        "difficulty": values["difficulty"],
        "locale": values["locale"],
        "languages": languages,
        "contract_risk": values["contract_risk"],
        "expected_decisions": decisions,
    }


def parse_behavior_cases(markdown: str, version: str | None = None) -> list[dict[str, Any]]:
    version = version or dataset_version()
    lines = markdown.splitlines()
    cases: list[dict[str, Any]] = []
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
        metadata = parse_metadata(section, case_id)
        try:
            prompt_heading = section.index("### Prompt")
            prompt, _ = extract_fenced_block(section, prompt_heading + 1)
            invariants_heading = section.index("### Required invariants")
        except ValueError as exc:
            raise ValueError(f"Malformed behavior case {case_id}: {exc}") from exc
        invariants: list[dict[str, str]] = []
        for line in section[invariants_heading + 1 :]:
            if line.startswith("### "):
                break
            if not line.startswith("- "):
                continue
            match = INVARIANT_ROW.match(line)
            if not match:
                raise ValueError(f"{case_id}: invariant metadata must be explicit: {line}")
            severity, grading, description = match.groups()
            invariants.append(
                {
                    "id": f"{case_id.lower()}-{len(invariants) + 1:02d}",
                    "description": description,
                    "severity": severity,
                    "grading": grading,
                }
            )
        if not invariants:
            raise ValueError(f"Behavior case {case_id} has no required invariants")
        tags = derive_tags(
            f"{title} {prompt}",
            [
                "behavior",
                metadata["mode"],
                metadata["difficulty"],
                f"locale-{metadata['locale'].lower()}",
                f"risk-{metadata['contract_risk']}",
                *(f"decision-{decision}" for decision in metadata["expected_decisions"]),
                *metadata["languages"],
            ],
        )
        cases.append(
            {
                "schema_version": "1.0",
                "dataset_version": version,
                "id": case_id,
                "suite": "behavior",
                "title": title,
                "prompt": prompt,
                "tags": tags,
                **metadata,
                "invariants": invariants,
            }
        )
        index = section_end
    return cases


def serialize_jsonl(records: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def count_values(cases: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for case in cases:
        value = case[field]
        if isinstance(value, list):
            counts.update(value)
        else:
            counts[str(value)] += 1
    return dict(sorted(counts.items()))


def build_outputs() -> dict[Path, str]:
    version = dataset_version()
    trigger_text = TRIGGER_SOURCE.read_text(encoding="utf-8")
    behavior_text = BEHAVIOR_SOURCE.read_text(encoding="utf-8")
    activation_cases = parse_activation_cases(trigger_text, version)
    behavior_cases = parse_behavior_cases(behavior_text, version)
    if not activation_cases or not behavior_cases:
        raise ValueError("Evaluation sources must contain activation and behavior cases")
    ids = [case["id"] for case in activation_cases + behavior_cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Evaluation case IDs must be unique")
    activation_jsonl = serialize_jsonl(activation_cases)
    behavior_jsonl = serialize_jsonl(behavior_cases)
    manifest = {
        "schema_version": "1.0",
        "dataset_version": version,
        "counts": {
            "activation": len(activation_cases),
            "behavior": len(behavior_cases),
            "invariants": sum(len(case["invariants"]) for case in behavior_cases),
        },
        "source_sha256": {
            "trigger-cases.md": sha256_text(trigger_text),
            "behavior-cases.md": sha256_text(behavior_text),
        },
        "output_sha256": {
            "cases/activation.jsonl": sha256_text(activation_jsonl),
            "cases/behavior.jsonl": sha256_text(behavior_jsonl),
        },
        "strata": {
            "activation_expected": {
                "false": sum(not case["expected_activation"] for case in activation_cases),
                "true": sum(case["expected_activation"] for case in activation_cases),
            },
            "activation_difficulty": count_values(activation_cases, "difficulty"),
            "activation_locale": count_values(activation_cases, "locale"),
            "behavior_mode": count_values(behavior_cases, "mode"),
            "behavior_difficulty": count_values(behavior_cases, "difficulty"),
            "behavior_locale": count_values(behavior_cases, "locale"),
            "behavior_language": count_values(behavior_cases, "languages"),
            "behavior_contract_risk": count_values(behavior_cases, "contract_risk"),
            "behavior_decision": count_values(behavior_cases, "expected_decisions"),
        },
    }
    return {
        ACTIVATION_OUTPUT: activation_jsonl,
        BEHAVIOR_OUTPUT: behavior_jsonl,
        MANIFEST_OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }


def write_outputs(outputs: dict[Path, str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
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
    mode.add_argument("--write", action="store_true", help="write generated datasets and manifest")
    mode.add_argument("--check", action="store_true", help="fail if generated datasets are stale")
    args = parser.parse_args()

    outputs = build_outputs()
    if args.write:
        write_outputs(outputs)
        return 0
    return check_outputs(outputs)


if __name__ == "__main__":
    raise SystemExit(main())
