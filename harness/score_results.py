#!/usr/bin/env python3
"""Score activation and invariant-graded evaluation results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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


def markdown_report(report: dict) -> str:
    lines = ["# Evaluation Report", "", f"Hard gate: {'PASS' if report['hard_gate_passed'] else 'FAIL'}", ""]
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
        lines.extend(["## Completion", "", "| Variant | Completed | Expected | Complete |", "|---|---:|---:|---|"])
        for variant, stats in report["completion"].items():
            lines.append(
                f"| {variant} | {stats['completed_cases']} | {stats['expected_cases']} | "
                f"{'yes' if stats['complete'] else 'no'} |"
            )
        lines.append("")
    if report["activation"]:
        lines.extend(["## Activation", "", "| Variant | Precision | Recall | Accuracy | TP | TN | FP | FN |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
        for variant, stats in report["activation"].items():
            lines.append(
                f"| {variant} | {stats['precision']} | {stats['recall']} | {stats['accuracy']} | "
                f"{stats['tp']} | {stats['tn']} | {stats['fp']} | {stats['fn']} |"
            )
        lines.append("")
    if report["behavior"]:
        lines.extend(["## Behavior", "", "| Variant | Pass rate | Critical failures | Critical ungraded | Ungraded | Hard gate |", "|---|---:|---:|---:|---:|---|"])
        for variant, stats in report["behavior"].items():
            lines.append(
                f"| {variant} | {stats['pass_rate']} | {stats['critical_failures']} | "
                f"{stats['critical_ungraded']} | {stats['ungraded']} | "
                f"{'PASS' if stats['hard_gate_passed'] else 'FAIL'} |"
            )
        lines.append("")
    if report["usage"]:
        lines.extend(
            [
                "## Usage",
                "",
                "| Variant | Results | Input tokens | Output tokens | Latency ms | Cost USD |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for variant, stats in report["usage"].items():
            lines.append(
                f"| {variant} | {stats['completed_results']} | {stats['input_tokens']['total']} | "
                f"{stats['output_tokens']['total']} | {stats['latency_ms']['total']} | "
                f"{stats['cost_usd']['total']} |"
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
            lines.append(
                f"| {key} | {stats['pass']} | {stats['fail']} | {stats['pass_rate']} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, nargs="+", required=True)
    parser.add_argument("--activation-cases", type=Path, default=ROOT / "evals/cases/activation.jsonl")
    parser.add_argument("--behavior-cases", type=Path, default=ROOT / "evals/cases/behavior.jsonl")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--policy", type=Path, help="versioned release policy JSON")
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
