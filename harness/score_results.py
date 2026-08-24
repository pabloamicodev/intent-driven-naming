#!/usr/bin/env python3
"""Score activation and invariant-graded evaluation results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.eval_core import (
    EvaluationDataError,
    apply_release_policy,
    load_case_map,
    read_jsonl,
    score_results,
)

ROOT = Path(__file__).resolve().parents[1]


class ReportInputError(ValueError):
    """Raised when an optional report attachment file cannot be loaded."""


def _load_report_attachment(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportInputError(f"cannot load {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReportInputError(f"{label} must be a JSON object")
    return value


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Evaluation Report",
        "",
        f"Hard gate: {'PASS' if report['hard_gate_passed'] else 'FAIL'}",
        "",
    ]
    if report["errors"]:
        lines.extend(["## Data Errors", ""])
        lines.extend(f"- {error}" for error in report["errors"])
        lines.append("")
    if report.get("policy"):
        policy = report["policy"]
        lines.extend(
            [
                "## Release Policy",
                "",
                f"{policy.get('name')} {policy.get('version')}: {'PASS' if policy['passed'] else 'FAIL'}",
                "",
            ]
        )
        lines.extend(f"- {violation}" for violation in policy["violations"])
        lines.extend(
            f"- {metric}: {value}" for metric, value in policy.get("observations", {}).items()
        )
        if policy["violations"]:
            lines.append("")
    if report["completion"]:
        lines.extend(
            [
                "## Completion",
                "",
                "| Cohort and replicate | Completed | Expected | Complete |",
                "|---|---:|---:|---|",
            ]
        )
        for cohort_replicate, stats in report["completion"].items():
            lines.append(
                f"| {cohort_replicate} | {stats['completed_cases']} | {stats['expected_cases']} | "
                f"{'yes' if stats['complete'] else 'no'} |"
            )
        lines.append("")
    if report["activation"]:
        lines.extend(
            [
                "## Activation",
                "",
                "| Cohort | Precision | Recall | Specificity | Balanced | Accuracy | 95% CI | FP rate |",
                "|---|---:|---:|---:|---:|---:|---|---:|",
            ]
        )
        for cohort, stats in report["activation"].items():
            lines.append(
                f"| {cohort} | {stats['precision']} | {stats['recall']} | {stats['specificity']} | "
                f"{stats['balanced_accuracy']} | {stats['accuracy']} | "
                f"{stats['accuracy_confidence_interval_95']} | {stats['false_positive_rate']} |"
            )
        lines.append("")
    if report["behavior"]:
        lines.extend(
            [
                "## Behavior",
                "",
                "| Cohort | Invariant pass | Case pass | Critical failures | Critical ungraded | Ungraded | Hard gate |",
                "|---|---:|---:|---:|---:|---:|---|",
            ]
        )
        for cohort, stats in report["behavior"].items():
            lines.append(
                f"| {cohort} | {stats['pass_rate']} | {stats['case_pass_rate']} | {stats['critical_failures']} | "
                f"{stats['critical_ungraded']} | {stats['ungraded']} | "
                f"{'PASS' if stats['hard_gate_passed'] else 'FAIL'} |"
            )
        lines.append("")
    if report.get("decisions"):
        lines.extend(
            [
                "## Decisions",
                "",
                "| Cohort | Exact match | Graded | Ungraded |",
                "|---|---:|---:|---:|",
            ]
        )
        for cohort, stats in report["decisions"].items():
            lines.append(
                f"| {cohort} | {stats['exact_match_rate']} | {stats['graded_cases']} | "
                f"{stats['ungraded_cases']} |"
            )
        lines.append("")
    if report.get("review_agreement"):
        agreement = report["review_agreement"]
        lines.extend(
            [
                "## Review Agreement",
                "",
                f"- Minimum reviews per candidate: {agreement.get('minimum_reviews_per_candidate')}",
                f"- Minimum human reviews per candidate: {agreement.get('minimum_human_reviews_per_candidate')}",
                f"- Raw grade agreement: {agreement.get('raw_grade_agreement')}",
                f"- Chance-corrected grade agreement: {agreement.get('chance_corrected_grade_agreement')}",
                f"- Decision-set agreement: {agreement.get('decision_set_agreement')}",
                "",
            ]
        )
    if report.get("pairwise_report"):
        pairwise = report["pairwise_report"]
        lines.extend(
            [
                "## Pairwise Review",
                "",
                f"- Resolved fraction: {pairwise.get('resolved_fraction')}",
                f"- With-skill win rate excluding ties: {pairwise.get('with_skill_win_rate_excluding_ties')}",
                f"- Minimum human reviews per pair: {pairwise.get('minimum_human_reviews_per_pair')}",
                "",
            ]
        )
    if report.get("experiment_verification"):
        experiment = report["experiment_verification"]
        lines.extend(
            [
                "## Preregistered Experiment",
                "",
                f"- Experiment: {experiment.get('experiment_id')}",
                f"- Verification: {'PASS' if experiment.get('valid') else 'FAIL'}",
                f"- Purpose: {experiment.get('purpose')}",
                f"- Held-out dataset: {experiment.get('held_out_dataset_present')}",
                f"- Systems: {experiment.get('systems')}",
                f"- Replicates: {experiment.get('replicates')}",
                "",
            ]
        )
    if report.get("configuration_integrity"):
        lines.extend(["## Configuration Integrity", ""])
        for system_id, integrity in report["configuration_integrity"].items():
            lines.append(
                f"- {system_id}: {'consistent' if integrity.get('consistent_across_variants_and_replicates') else 'DRIFT'}"
            )
        lines.append("")
    if report["usage"]:
        lines.extend(
            [
                "## Usage",
                "",
                "| Cohort | Results | Input tokens | Output tokens | Context words | Turns | Tool calls | Latency ms | Cost USD |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for variant, stats in report["usage"].items():
            lines.append(
                f"| {variant} | {stats['completed_results']} | {stats['input_tokens']['total']} | "
                f"{stats['output_tokens']['total']} | {stats['skill_context_words']['total']} | "
                f"{stats['turns']['total']} | {stats['tool_calls']['total']} | "
                f"{stats['latency_ms']['total']} | "
                f"{stats['cost_usd']['total']} |"
            )
        lines.append("")
    if report.get("resource_loading"):
        lines.extend(
            [
                "## Resource Loading",
                "",
                "| Cohort | Reporting rate | Core rate | Mean resources | Unknown loads | Unexpected activation loads |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for cohort, stats in report["resource_loading"].items():
            unknown = sum(stats["unknown_resources"].values())
            lines.append(
                f"| {cohort} | {stats['reporting_rate']} | {stats['core_complete_rate']} | "
                f"{stats['mean_resources_per_result']} | {unknown} | "
                f"{stats['unexpected_activation_resource_results']} |"
            )
        lines.append("")
    if report["by_tag"]:
        lines.extend(
            [
                "## Behavior by Tag",
                "",
                "| Variant and tag | Pass | Fail | Pass rate |",
                "|---|---:|---:|---:|",
            ]
        )
        for key, stats in report["by_tag"].items():
            lines.append(f"| {key} | {stats['pass']} | {stats['fail']} | {stats['pass_rate']} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, nargs="+", required=True)
    parser.add_argument(
        "--activation-cases", type=Path, default=ROOT / "evals/cases/activation.jsonl"
    )
    parser.add_argument("--behavior-cases", type=Path, default=ROOT / "evals/cases/behavior.jsonl")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--policy", type=Path, help="versioned release policy JSON")
    parser.add_argument(
        "--review-agreement",
        type=Path,
        help="review agreement JSON produced by merge_reviews.py",
    )
    parser.add_argument(
        "--pairwise-report",
        type=Path,
        help="pairwise JSON produced by score_pairwise.py",
    )
    parser.add_argument(
        "--experiment-verification",
        type=Path,
        help="verification JSON produced by verify_experiment.py",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="fail unless every loaded case completed for every result variant",
    )
    parser.add_argument("--allow-failures", action="store_true")
    args = parser.parse_args()

    try:
        cases = load_case_map([args.activation_cases, args.behavior_cases])
        results = [record for path in args.results for record in read_jsonl(path)]
    except EvaluationDataError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    report = score_results(cases, results, require_complete=args.require_complete)
    try:
        if args.review_agreement:
            report["review_agreement"] = _load_report_attachment(
                args.review_agreement, "review agreement"
            )
        if args.pairwise_report:
            report["pairwise_report"] = _load_report_attachment(
                args.pairwise_report, "pairwise report"
            )
        if args.experiment_verification:
            report["experiment_verification"] = _load_report_attachment(
                args.experiment_verification, "experiment verification"
            )
    except ReportInputError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.policy:
        try:
            policy = json.loads(args.policy.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"cannot load release policy: {exc}", file=sys.stderr)
            return 2
        report = apply_release_policy(report, policy)
    rendered_json = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    rendered_markdown = markdown_report(report)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered_json, encoding="utf-8", newline="\n")
    else:
        print(rendered_json, end="")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(rendered_markdown, encoding="utf-8", newline="\n")
    if report["hard_gate_passed"] or args.allow_failures:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
