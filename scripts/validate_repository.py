#!/usr/bin/env python3
"""Validate the skill package, specifications, datasets, routes, and governance files."""

from __future__ import annotations

import argparse
import itertools
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
TRIGGER_ID = re.compile(r"^\| (T\d{2}) \|")
BEHAVIOR_ID = re.compile(r"^## (B\d{2}) —")


def word_count(path: Path) -> int:
    return len(re.findall(r"\S+", path.read_text(encoding="utf-8")))


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None


def load_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        errors.append(f"missing dataset: {path.relative_to(ROOT)}")
        return records
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}:{line_number}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path.relative_to(ROOT)}:{line_number}: expected JSON object")
            continue
        records.append(record)
    return records


def prose_paragraphs(markdown: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    in_fence = False

    def flush() -> None:
        if current:
            normalized = " ".join(" ".join(current).split())
            if len(normalized) >= 120:
                paragraphs.append(normalized)
            current.clear()

    for line in markdown.splitlines():
        if line.startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if stripped.startswith(("#", "- ", "* ", ">", "|")) or re.match(r"^\d+\.\s", stripped):
            flush()
            continue
        current.append(stripped)
    flush()
    return paragraphs


def validate_markdown(errors: list[str], warnings: list[str]) -> dict[str, int]:
    markdown_files = sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(
            excluded in path.parts
            for excluded in (".git", ".venv", ".tox", "node_modules", "__pycache__")
        )
    )
    reference_files = sorted((ROOT / "references").glob("*.md"))
    linked_references: set[Path] = set()
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        headings = [match.groups() for line in text.splitlines() if (match := HEADING.match(line))]
        h1_count = sum(1 for level, _ in headings if level == "#")
        if h1_count != 1:
            errors.append(f"{path.relative_to(ROOT)}: expected exactly one H1, found {h1_count}")
        if path.parent == ROOT / "references":
            h2_names = [title for level, title in headings if level == "##"]
            duplicates = [name for name, count in Counter(h2_names).items() if count > 1]
            for name in duplicates:
                errors.append(f"{path.relative_to(ROOT)}: duplicate H2 heading '{name}'")
            paragraph_counts = Counter(prose_paragraphs(text))
            for paragraph, count in paragraph_counts.items():
                if count > 1:
                    errors.append(
                        f"{path.relative_to(ROOT)}: duplicated prose paragraph x{count}: {paragraph[:80]}..."
                    )
        for target in MARKDOWN_LINK.findall(text):
            clean = target.strip("<>").split("#", 1)[0]
            if not clean or re.match(r"^[a-z]+://", clean) or clean.startswith(("mailto:", "/")):
                continue
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link '{target}'")
            try:
                relative = resolved.relative_to((ROOT / "references").resolve())
            except ValueError:
                continue
            if relative.suffix == ".md":
                linked_references.add(resolved)
    for reference in reference_files:
        if reference.resolve() not in linked_references:
            errors.append(f"{reference.relative_to(ROOT)}: reference is not routed from any Markdown file")
    if len(markdown_files) > 40:
        warnings.append(f"large Markdown surface: {len(markdown_files)} files")
    return {"markdown_files": len(markdown_files), "references": len(reference_files)}


def validate_frontmatter(errors: list[str]) -> dict[str, int]:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    line_count = len(skill.splitlines())
    if line_count > 500:
        errors.append(f"SKILL.md: {line_count} lines exceeds the Agent Skills limit of 500")
    if not skill.startswith("---\n"):
        errors.append("SKILL.md: missing YAML frontmatter")
        return {}
    parts = skill.split("---", 2)
    if len(parts) < 3:
        errors.append("SKILL.md: unterminated YAML frontmatter")
        return {}
    frontmatter = parts[1]
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    skill_name = name_match.group(1).strip() if name_match else ""
    if skill_name != "intent-driven-naming":
        errors.append("SKILL.md: unexpected or missing name")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_name):
        errors.append("SKILL.md: name violates the portable Agent Skills naming grammar")
    if skill_name and skill_name != ROOT.name:
        errors.append("SKILL.md: name must match the parent directory")
    if not description_match:
        errors.append("SKILL.md: missing description")
        description_length = 0
    else:
        description_length = len(description_match.group(1).strip())
        if description_length > 1024:
            errors.append(f"SKILL.md: description too long ({description_length})")
    metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    short_match = re.search(r'^\s*short_description:\s*"([^"]+)"', metadata, re.MULTILINE)
    if not short_match:
        errors.append("agents/openai.yaml: missing short_description")
        short_length = 0
    else:
        short_length = len(short_match.group(1))
        if not 25 <= short_length <= 64:
            errors.append(f"agents/openai.yaml: short_description length is {short_length}, expected 25-64")
    return {
        "description_length": description_length,
        "short_description_length": short_length,
        "skill_lines": line_count,
    }


def validate_routes(errors: list[str]) -> dict[str, Any]:
    routes = load_json(ROOT / "specification" / "routes.json", errors)
    budgets = load_json(ROOT / "specification" / "context-budgets.json", errors)
    if not isinstance(routes, dict) or not isinstance(budgets, dict):
        return {}
    all_paths: set[str] = set(routes.get("always", []))
    for group_name in ("conditional_core", "modes", "features", "profiles"):
        group = routes.get(group_name, {})
        if not isinstance(group, dict):
            errors.append(f"specification/routes.json: {group_name} must be an object")
            continue
        for paths in group.values():
            if not isinstance(paths, list):
                errors.append(f"specification/routes.json: {group_name} entries must be arrays")
                continue
            all_paths.update(paths)
    counts: dict[str, int] = {}
    for relative in sorted(all_paths):
        path = ROOT / relative
        if not path.exists():
            errors.append(f"specification/routes.json: missing routed file {relative}")
            continue
        counts[relative] = word_count(path)
    budget_values = budgets.get("budgets", {})
    entrypoint_budget = budget_values.get("entrypoint")
    if isinstance(entrypoint_budget, int) and counts.get("SKILL.md", 0) > entrypoint_budget:
        errors.append(f"SKILL.md exceeds entrypoint budget: {counts['SKILL.md']} > {entrypoint_budget}")
    single_budget = budget_values.get("single-reference")
    exceptions = budgets.get("exceptions", {})
    for relative, count in counts.items():
        if not relative.startswith("references/"):
            continue
        limit = exceptions.get(relative, single_budget)
        if isinstance(limit, int) and count > limit:
            errors.append(f"{relative} exceeds reference budget: {count} > {limit}")

    always = routes.get("always", [])
    always_words = sum(counts.get(path, 0) for path in dict.fromkeys(always))
    always_budget = budget_values.get("always-loaded")
    if isinstance(always_budget, int) and always_words > always_budget:
        errors.append(f"always-loaded route exceeds budget: {always_words} > {always_budget}")
    runtime_words = sum(counts.values())
    runtime_budget = budget_values.get("runtime-instructions")
    if isinstance(runtime_budget, int) and runtime_words > runtime_budget:
        errors.append(f"runtime instructions exceed budget: {runtime_words} > {runtime_budget}")
    modes = list(routes.get("modes", {}).items())
    features = list(routes.get("features", {}).items())
    profiles = list(routes.get("profiles", {}).items())
    feature_choices = [()] + [(item,) for item in features] + [tuple(features)]
    standard_routes: list[tuple[str, int]] = []
    for (mode_name, mode_paths), feature_choice, (profile_name, profile_paths) in itertools.product(
        modes, feature_choices, profiles
    ):
        paths = list(always) + list(mode_paths) + list(profile_paths)
        feature_names: list[str] = []
        for feature_name, feature_paths in feature_choice:
            feature_names.append(feature_name)
            paths.extend(feature_paths)
        unique_paths = list(dict.fromkeys(paths))
        total = sum(counts.get(path, 0) for path in unique_paths)
        label = f"{mode_name}+{'+'.join(feature_names) if feature_names else 'no-feature'}+{profile_name}"
        standard_routes.append((label, total))
    max_standard_label, max_standard = max(standard_routes, key=lambda item: item[1])
    standard_budget = budget_values.get("standard-route")
    if isinstance(standard_budget, int) and max_standard > standard_budget:
        errors.append(f"maximum standard route exceeds budget: {max_standard_label} {max_standard} > {standard_budget}")
    conditional_paths = [path for paths in routes.get("conditional_core", {}).values() for path in paths]
    maximum_profiles = budgets.get("maximum_simultaneous_profiles")
    if (
        isinstance(maximum_profiles, bool)
        or not isinstance(maximum_profiles, int)
        or maximum_profiles < 1
    ):
        errors.append("context budget maximum_simultaneous_profiles must be a positive integer")
        maximum_profiles = 1
    polyglot_routes: list[tuple[str, int]] = []
    for (mode_name, mode_paths), feature_choice in itertools.product(modes, feature_choices):
        for profile_count in range(1, min(maximum_profiles, len(profiles)) + 1):
            for profile_choice in itertools.combinations(profiles, profile_count):
                paths = list(always) + list(mode_paths) + list(conditional_paths)
                feature_names: list[str] = []
                for feature_name, feature_paths in feature_choice:
                    feature_names.append(feature_name)
                    paths.extend(feature_paths)
                profile_names: list[str] = []
                for profile_name, profile_paths in profile_choice:
                    profile_names.append(profile_name)
                    paths.extend(profile_paths)
                total = sum(counts.get(path, 0) for path in dict.fromkeys(paths))
                label = (
                    f"{mode_name}+{'+'.join(feature_names) if feature_names else 'no-feature'}+"
                    f"{'+'.join(profile_names)}"
                )
                polyglot_routes.append((label, total))
    max_polyglot_label, max_extended = max(polyglot_routes, key=lambda item: item[1])
    extended_budget = budget_values.get("extended-route")
    if isinstance(extended_budget, int) and max_extended > extended_budget:
        errors.append(
            f"maximum extended route exceeds budget: {max_polyglot_label} "
            f"{max_extended} > {extended_budget}"
        )
    return {
        "file_words": counts,
        "always_loaded_words": always_words,
        "runtime_instruction_words": runtime_words,
        "max_standard_route": {"name": max_standard_label, "words": max_standard},
        "max_extended_route": {"name": max_polyglot_label, "words": max_extended},
        "max_extended_route_words": max_extended,
        "maximum_simultaneous_profiles": maximum_profiles,
    }


def validate_evaluations(errors: list[str]) -> dict[str, int]:
    sys.path.insert(0, str(ROOT))
    from harness.eval_core import validate_case

    activation = load_jsonl(ROOT / "evals" / "cases" / "activation.jsonl", errors)
    behavior = load_jsonl(ROOT / "evals" / "cases" / "behavior.jsonl", errors)
    ids: set[str] = set()
    for record in activation + behavior:
        record_errors = validate_case(record)
        errors.extend(f"eval {record.get('id', '?')}: {error}" for error in record_errors)
        case_id = record.get("id")
        if case_id in ids:
            errors.append(f"duplicate evaluation id {case_id}")
        ids.add(case_id)
    trigger_source_ids = {
        match.group(1)
        for line in (ROOT / "evals" / "trigger-cases.md").read_text(encoding="utf-8").splitlines()
        if (match := TRIGGER_ID.match(line))
    }
    behavior_source_ids = {
        match.group(1)
        for line in (ROOT / "evals" / "behavior-cases.md").read_text(encoding="utf-8").splitlines()
        if (match := BEHAVIOR_ID.match(line))
    }
    if trigger_source_ids != {record.get("id") for record in activation}:
        errors.append("activation JSONL IDs do not match trigger-cases.md")
    if behavior_source_ids != {record.get("id") for record in behavior}:
        errors.append("behavior JSONL IDs do not match behavior-cases.md")
    fixture_manifest = load_json(ROOT / "evals" / "fixtures" / "manifest.json", errors)
    fixture_count = 0
    if isinstance(fixture_manifest, dict) and isinstance(fixture_manifest.get("fixtures"), list):
        fixture_count = len(fixture_manifest["fixtures"])
        fixture_ids: set[str] = set()
        behavior_ids = {record.get("id") for record in behavior}
        for fixture in fixture_manifest["fixtures"]:
            if not isinstance(fixture, dict):
                errors.append("fixture manifest entries must be objects")
                continue
            fixture_id = fixture.get("id")
            if fixture_id in fixture_ids:
                errors.append(f"duplicate fixture id {fixture_id}")
            fixture_ids.add(fixture_id)
            unknown_cases = set(fixture.get("related_behavior_cases", [])) - behavior_ids
            if unknown_cases:
                errors.append(f"fixture {fixture_id} references unknown behavior cases {sorted(unknown_cases)}")
    manifest = load_json(ROOT / "evals" / "manifest.json", errors)
    corpus_policy = load_json(ROOT / "specification" / "corpus-policy.json", errors)
    if isinstance(manifest, dict) and isinstance(corpus_policy, dict):
        if corpus_policy.get("dataset_version") != manifest.get("dataset_version"):
            errors.append("corpus policy dataset_version does not match evaluation manifest")
        counts = dict(manifest.get("counts", {}))
        counts["fixtures"] = fixture_count
        for label, minimum in corpus_policy.get("minimum_counts", {}).items():
            actual = counts.get(label)
            if not isinstance(actual, int) or actual < minimum:
                errors.append(f"corpus {label} count {actual} is below required minimum {minimum}")
        strata = manifest.get("strata", {})
        expected = strata.get("activation_expected", {})
        if isinstance(expected, dict):
            imbalance = abs(expected.get("true", 0) - expected.get("false", 0))
            maximum_imbalance = corpus_policy.get("maximum_activation_expected_imbalance")
            if isinstance(maximum_imbalance, int) and imbalance > maximum_imbalance:
                errors.append(
                    f"activation expected-label imbalance {imbalance} exceeds {maximum_imbalance}"
                )
        for stratum, minimum in corpus_policy.get("minimum_unique_values", {}).items():
            values = strata.get(stratum, {})
            actual = len(values) if isinstance(values, dict) else 0
            if actual < minimum:
                errors.append(
                    f"corpus stratum {stratum} has {actual} values, below required {minimum}"
                )
        for stratum, minimums in corpus_policy.get("minimum_strata", {}).items():
            actuals = strata.get(stratum, {})
            for value, minimum in minimums.items():
                actual = actuals.get(value, 0) if isinstance(actuals, dict) else 0
                if actual < minimum:
                    errors.append(
                        f"corpus stratum {stratum}.{value} count {actual} is below {minimum}"
                    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for count, label in ((len(activation), "activation"), (len(behavior), "behavior")):
        if str(count) not in readme:
            errors.append(f"README.md does not mention current {label} count {count}")
    export_check = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "export_evals.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if export_check.returncode != 0:
        errors.append(export_check.stderr.strip() or "generated evaluation datasets are stale")
    return {
        "activation_cases": len(activation),
        "behavior_cases": len(behavior),
        "fixture_cases": fixture_count,
    }


def validate_governance(errors: list[str]) -> None:
    required = [
        "VERSION",
        "LICENSE",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "GOVERNANCE.md",
        "CODE_OF_CONDUCT.md",
        ".github/workflows/ci.yml",
    ]
    for relative in required:
        if not (ROOT / relative).exists():
            errors.append(f"missing adoption file: {relative}")
    version_path = ROOT / "VERSION"
    if version_path.exists():
        version = version_path.read_text(encoding="utf-8").strip()
        if not VERSION_PATTERN.fullmatch(version):
            errors.append(f"VERSION is not semantic: {version}")
    for schema in sorted((ROOT / "specification").glob("*.json")):
        load_json(schema, errors)
    policy = load_json(ROOT / "specification" / "release-policy.json", errors)
    if not isinstance(policy, dict):
        errors.append("specification/release-policy.json must be an object")
        return
    if version_path.exists() and policy.get("version") != version_path.read_text(encoding="utf-8").strip():
        errors.append("release policy version does not match VERSION")
    if policy.get("schema_version") != "2.0":
        errors.append("release policy schema_version must be 2.0")
    dataset_version_path = ROOT / "evals" / "DATASET_VERSION"
    if (
        dataset_version_path.exists()
        and policy.get("dataset_version") != dataset_version_path.read_text(encoding="utf-8").strip()
    ):
        errors.append("release policy dataset_version does not match evals/DATASET_VERSION")
    variants = policy.get("required_variants")
    if not isinstance(variants, list) or any(not isinstance(value, str) for value in variants):
        errors.append("release policy required_variants must be a string array")
    elif set(variants) != {"with-skill", "previous-skill", "without-skill"}:
        errors.append(
            "release policy must require with-skill, previous-skill, and without-skill variants"
        )
    if policy.get("gated_variant") != "with-skill":
        errors.append("release policy must gate the with-skill variant")
    minimum_replicates = policy.get("minimum_replicates")
    if (
        isinstance(minimum_replicates, bool)
        or not isinstance(minimum_replicates, int)
        or minimum_replicates < 3
    ):
        errors.append("release policy must require at least three replicates")
    activation = policy.get("activation")
    expected_activation_fields = {
        "minimum_precision",
        "minimum_recall",
        "minimum_specificity",
        "minimum_balanced_accuracy",
        "minimum_accuracy",
        "maximum_false_positive_rate",
        "minimum_slice_accuracy",
        "maximum_slice_false_positive_rate",
    }
    if not isinstance(activation, dict) or set(activation) != expected_activation_fields:
        errors.append("release policy activation thresholds are incomplete")
    elif any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1
        for value in activation.values()
    ):
        errors.append("release policy activation thresholds must be ratios")
    behavior = policy.get("behavior")
    if not isinstance(behavior, dict):
        errors.append("release policy behavior threshold is invalid")
    else:
        ratio_fields = (
            "minimum_pass_rate",
            "minimum_case_pass_rate",
            "minimum_decision_exact_match_rate",
            "minimum_slice_pass_rate",
        )
        maximum_ungraded = behavior.get("maximum_ungraded")
        minimum_slice_observations = behavior.get("minimum_slice_observations")
        if any(
            isinstance(behavior.get(field), bool)
            or not isinstance(behavior.get(field), (int, float))
            or not 0 <= behavior[field] <= 1
            for field in ratio_fields
        ) or (
            isinstance(maximum_ungraded, bool)
            or not isinstance(maximum_ungraded, int)
            or maximum_ungraded < 0
            or isinstance(minimum_slice_observations, bool)
            or not isinstance(minimum_slice_observations, int)
            or minimum_slice_observations < 1
        ):
            errors.append("release policy behavior threshold is invalid")
    review = policy.get("review")
    if not isinstance(review, dict):
        errors.append("release policy review thresholds are invalid")
    else:
        minimum_reviews = review.get("minimum_reviews_per_candidate")
        agreement_fields = (
            "minimum_raw_grade_agreement",
            "minimum_chance_corrected_grade_agreement",
            "minimum_decision_set_agreement",
        )
        if (
            isinstance(minimum_reviews, bool)
            or not isinstance(minimum_reviews, int)
            or minimum_reviews < 2
            or any(
                isinstance(review.get(field), bool)
                or not isinstance(review.get(field), (int, float))
                or not -1 <= review[field] <= 1
                for field in agreement_fields
            )
        ):
            errors.append("release policy review thresholds are invalid")
    pairwise = policy.get("pairwise")
    expected_pairwise_fields = {
        "minimum_resolved_fraction",
        "minimum_with_skill_win_rate_excluding_ties",
        "minimum_raw_reviewer_agreement",
    }
    if not isinstance(pairwise, dict) or set(pairwise) != expected_pairwise_fields or any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1
        for value in pairwise.values()
    ):
        errors.append("release policy pairwise thresholds are invalid")
    comparison = policy.get("comparison")
    if not isinstance(comparison, dict) or comparison.get("baseline_variant") != "without-skill":
        errors.append("release policy comparison baseline is invalid")
    elif any(
        isinstance(comparison.get(key), bool)
        or not isinstance(comparison.get(key), (int, float))
        for key in (
            "minimum_activation_accuracy_delta",
            "minimum_activation_accuracy_lower_bound",
            "minimum_behavior_pass_rate_delta",
            "minimum_behavior_pass_rate_lower_bound",
        )
    ):
        errors.append("release policy comparison deltas are invalid")
    efficiency = policy.get("efficiency")
    expected_efficiency_fields = {
        "comparison_variant",
        "required_usage_fields",
        "minimum_resource_reporting_rate",
        "minimum_core_resource_rate",
        "maximum_unknown_resources",
        "maximum_unnecessary_resources",
        "maximum_overloaded_profile_results",
        "maximum_unexpected_activation_resource_results",
        "maximum_input_token_ratio",
        "maximum_skill_context_word_ratio",
        "maximum_turn_ratio",
        "maximum_standard_route_words",
        "maximum_extended_route_words",
        "maximum_runtime_instruction_words",
    }
    if not isinstance(efficiency, dict) or set(efficiency) != expected_efficiency_fields:
        errors.append("release policy efficiency thresholds are incomplete")
    else:
        usage_fields = efficiency.get("required_usage_fields")
        required_usage_fields = {
            "input_tokens", "output_tokens", "latency_ms", "skill_context_words", "turns", "tool_calls"
        }
        if (
            efficiency.get("comparison_variant") != "previous-skill"
            or not isinstance(usage_fields, list)
            or not required_usage_fields.issubset(usage_fields)
            or any(
                isinstance(efficiency.get(field), bool)
                or not isinstance(efficiency.get(field), (int, float))
                or not 0 <= efficiency[field] <= 1
                for field in ("minimum_resource_reporting_rate", "minimum_core_resource_rate")
            )
            or isinstance(efficiency.get("maximum_unknown_resources"), bool)
            or not isinstance(efficiency.get("maximum_unknown_resources"), int)
            or efficiency["maximum_unknown_resources"] < 0
            or isinstance(efficiency.get("maximum_unnecessary_resources"), bool)
            or not isinstance(efficiency.get("maximum_unnecessary_resources"), int)
            or efficiency["maximum_unnecessary_resources"] < 0
            or isinstance(efficiency.get("maximum_overloaded_profile_results"), bool)
            or not isinstance(efficiency.get("maximum_overloaded_profile_results"), int)
            or efficiency["maximum_overloaded_profile_results"] < 0
            or isinstance(
                efficiency.get("maximum_unexpected_activation_resource_results"), bool
            )
            or not isinstance(
                efficiency.get("maximum_unexpected_activation_resource_results"), int
            )
            or efficiency["maximum_unexpected_activation_resource_results"] < 0
            or any(
                isinstance(efficiency.get(field), bool)
                or not isinstance(efficiency.get(field), (int, float))
                or efficiency[field] <= 0
                for field in (
                    "maximum_input_token_ratio",
                    "maximum_skill_context_word_ratio",
                    "maximum_turn_ratio",
                )
            )
            or any(
                isinstance(efficiency.get(field), bool)
                or not isinstance(efficiency.get(field), int)
                or efficiency[field] < 1
                for field in (
                    "maximum_standard_route_words",
                    "maximum_extended_route_words",
                    "maximum_runtime_instruction_words",
                )
            )
        ):
            errors.append("release policy efficiency thresholds are invalid")
        route_metrics = validate_routes([])
        standard_limit = efficiency.get("maximum_standard_route_words")
        extended_limit = efficiency.get("maximum_extended_route_words")
        runtime_limit = efficiency.get("maximum_runtime_instruction_words")
        if (
            route_metrics
            and isinstance(standard_limit, int)
            and isinstance(extended_limit, int)
            and isinstance(runtime_limit, int)
        ):
            if route_metrics["max_standard_route"]["words"] > standard_limit:
                errors.append("release policy standard route budget is exceeded")
            if route_metrics["max_extended_route_words"] > extended_limit:
                errors.append("release policy extended route budget is exceeded")
            if route_metrics["runtime_instruction_words"] > runtime_limit:
                errors.append("release policy runtime instruction budget is exceeded")
    required_fields = policy.get("required_implementation_fields")
    expected_fields = {
        "adapter",
        "adapter_version",
        "agent",
        "agent_version",
        "model",
        "model_version",
        "reasoning",
    }
    if not isinstance(required_fields, list) or not expected_fields.issubset(required_fields):
        errors.append("release policy implementation metadata is incomplete")


def validate_placeholders(errors: list[str]) -> None:
    pattern = re.compile(r"\b(TODO|TBD|PLACEHOLDER)\b", re.IGNORECASE)
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(
            excluded in path.parts
            for excluded in (
                ".git", ".venv", ".tox", "node_modules", "__pycache__", "benchmarks"
            )
        ):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in {".md", ".json", ".jsonl", ".yaml", ".yml", ".py", ".txt"}:
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if pattern.search(line):
                errors.append(f"{path.relative_to(ROOT)}:{line_number}: unresolved placeholder token")


def validate_repository() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {}
    metrics.update(validate_markdown(errors, warnings))
    metrics.update(validate_frontmatter(errors))
    metrics["routes"] = validate_routes(errors)
    metrics.update(validate_evaluations(errors))
    validate_governance(errors)
    validate_placeholders(errors)
    return {
        "schema_version": "1.0",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    report = validate_repository()
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered, encoding="utf-8", newline="\n")
    if report["valid"]:
        metrics = report["metrics"]
        print(
            "repository validation passed: "
            f"references={metrics.get('references')} "
            f"activation={metrics.get('activation_cases')} "
            f"behavior={metrics.get('behavior_cases')}"
        )
        routes = metrics.get("routes", {})
        if routes:
            print(
                f"context budget: standard={routes['max_standard_route']['words']} "
                f"extended={routes['max_extended_route_words']} words"
            )
        return 0
    print(rendered, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
