#!/usr/bin/env python3
"""Reference JSONL adapter for isolated, non-interactive Codex CLI evaluations."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESPONSE_SCHEMA = ROOT / "adapters" / "codex-response.schema.json"
SAFE_REASONING_EFFORT = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.create_artifact_bundle import build_bundle


def codex_version(command: list[str]) -> str:
    completed = subprocess.run(
        [*command, "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=30,
    )
    return completed.stdout.strip()


def install_runtime_skill(source: Path, workspace: Path) -> None:
    target = workspace / ".agents" / "skills" / "intent-driven-naming"
    target.mkdir(parents=True, exist_ok=True)
    runtime_paths = (
        Path("SKILL.md"),
        Path("agents"),
        Path("references"),
        Path("scripts/runtime"),
        Path("specification/semantic-record.schema.json"),
        Path("specification/rename-plan.schema.json"),
        Path("LICENSE"),
        Path("VERSION"),
    )
    for relative in runtime_paths:
        candidate = source / relative
        if not candidate.exists():
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if candidate.is_dir():
            shutil.copytree(candidate, destination)
        else:
            shutil.copy2(candidate, destination)


def recursive_metric(payload: Any, key: str) -> list[float]:
    values: list[float] = []
    if isinstance(payload, dict):
        for candidate_key, value in payload.items():
            if candidate_key == key and isinstance(value, (int, float)) and not isinstance(value, bool):
                values.append(float(value))
            else:
                values.extend(recursive_metric(value, key))
    elif isinstance(payload, list):
        for value in payload:
            values.extend(recursive_metric(value, key))
    return values


def parse_usage(
    stdout: str, latency_ms: float, skill_context_words: int = 0
) -> dict[str, int | float | None]:
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except (json.JSONDecodeError, RecursionError):
            continue
    metrics: dict[str, int | float | None] = {
        "latency_ms": round(latency_ms, 3),
        "cost_usd": None,
        "skill_context_words": skill_context_words,
        "turns": 1,
        "tool_calls": sum(
            1
            for event in events
            if isinstance(event, dict)
            and any(
                marker in str(event.get("type", "")).lower()
                for marker in ("tool_call", "command_execution", "mcp_tool")
            )
        ),
    }
    for key in ("input_tokens", "output_tokens"):
        values = recursive_metric(events, key)
        metrics[key] = int(max(values)) if values else None
    cost_values = recursive_metric(events, "cost_usd")
    if cost_values:
        metrics["cost_usd"] = max(cost_values)
    return metrics


def create_bundle(workspace: Path, output_root: Path, request: dict[str, Any]) -> dict[str, Any]:
    candidates = [
        path
        for path in workspace.rglob("*")
        if path.is_file() and ".agents" not in path.relative_to(workspace).parts
    ]
    if not candidates:
        return {"format": "none", "path": None, "sha256": None, "verifier_report_path": None}
    includes = [path.relative_to(workspace).as_posix() for path in candidates]
    try:
        bundle = build_bundle(workspace, includes, 1_000_000)
    except ValueError as exc:
        raise RuntimeError(f"cannot create sanitized artifact bundle: {exc}") from exc
    identity = "\0".join(
        str(request[field])
        for field in ("run_id", "system_id", "variant", "replicate_id", "attempt")
    )
    directory = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
    relative_output = Path(directory) / f"{request['case']['id']}.json"
    output = output_root / relative_output
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    output.write_text(rendered, encoding="utf-8", newline="\n")
    return {
        "format": "directory",
        "path": relative_output.as_posix(),
        "sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
        "verifier_report_path": None,
    }


def evaluate(request: dict[str, Any], args: argparse.Namespace, version: str) -> dict[str, Any]:
    case = request["case"]
    implementation = {
        "adapter": "intent-driven-naming-codex-cli",
        "adapter_version": "2.0.0",
        "agent": "codex-cli",
        "agent_version": version,
        "model": args.model,
        "model_version": args.model_version,
        "reasoning": args.reasoning,
    }
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(
        prefix="intent-naming-codex-", ignore_cleanup_errors=True
    ) as temporary_directory:
        workspace = Path(temporary_directory) / "workspace"
        workspace.mkdir()
        if request["variant"] in {"with-skill", "previous-skill"}:
            install_runtime_skill(Path(request["skill_path"]), workspace)
        output_path = Path(temporary_directory) / "last-message.json"
        prompt = (
            "Complete the user request below. Work only inside the isolated workspace. "
            "Return the required JSON object. Set selected_skill to true only if you actually used "
            "a repository skill while solving the request. List the exact relative SKILL.md or "
            "reference paths you loaded. Put the complete user-facing answer in answer.\n\n"
            f"USER REQUEST:\n{case['prompt']}"
        )
        command = [
            *args.codex_command,
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--skip-git-repo-check",
            "--json",
            "--color",
            "never",
            "--sandbox",
            "workspace-write",
            "--cd",
            str(workspace),
            "--model",
            args.model,
            "--config",
            f'model_reasoning_effort="{args.reasoning}"',
            "--output-schema",
            str(RESPONSE_SCHEMA),
            "--output-last-message",
            str(output_path),
            "-",
        ]
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                timeout=args.case_timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {
                "protocol_version": 1,
                "case_id": case["id"],
                "status": "failed",
                "implementation": implementation,
                "error": str(exc),
            }
        latency_ms = (time.perf_counter() - started) * 1000
        if completed.returncode != 0 or not output_path.exists():
            error = completed.stderr.strip() or completed.stdout[-4000:] or f"codex exited {completed.returncode}"
            return {
                "protocol_version": 1,
                "case_id": case["id"],
                "status": "failed",
                "implementation": implementation,
                "usage": parse_usage(completed.stdout, latency_ms),
                "error": error,
            }
        try:
            answer = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                "protocol_version": 1,
                "case_id": case["id"],
                "status": "failed",
                "implementation": implementation,
                "usage": parse_usage(completed.stdout, latency_ms),
                "error": f"invalid structured Codex response: {exc}",
            }
        try:
            artifact_bundle = create_bundle(workspace, args.artifact_output_root, request)
        except (OSError, RuntimeError) as exc:
            return {
                "protocol_version": 1,
                "case_id": case["id"],
                "status": "failed",
                "implementation": implementation,
                "usage": parse_usage(completed.stdout, latency_ms),
                "error": str(exc),
            }
        skill_context_words = 0
        source = Path(request["skill_path"]).resolve()
        for relative in answer["loaded_resources"]:
            resource = (source / relative).resolve()
            try:
                resource.relative_to(source)
            except ValueError:
                continue
            if resource.is_file():
                skill_context_words += len(resource.read_text(encoding="utf-8").split())
        return {
            "protocol_version": 1,
            "case_id": case["id"],
            "status": "completed",
            "selected_skill": answer["selected_skill"],
            "output_text": answer["answer"],
            "loaded_resources": answer["loaded_resources"],
            "artifact_bundle": artifact_bundle,
            "usage": parse_usage(completed.stdout, latency_ms, skill_context_words),
            "implementation": implementation,
            "error": None,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default="codex")
    parser.add_argument(
        "--codex-prefix-arg",
        action="append",
        default=[],
        help="argument inserted after --codex; primarily useful for wrapper-based testing",
    )
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-version", required=True)
    parser.add_argument("--reasoning", default="high")
    parser.add_argument("--artifact-output-root", type=Path, required=True)
    parser.add_argument("--case-timeout-seconds", type=int, default=900)
    args = parser.parse_args()
    if not SAFE_REASONING_EFFORT.match(args.reasoning):
        print("--reasoning must match ^[A-Za-z0-9_-]{1,32}$", file=sys.stderr)
        return 2
    args.codex_command = [args.codex, *args.codex_prefix_arg]
    try:
        version = codex_version(args.codex_command)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"cannot execute Codex CLI: {exc}", file=sys.stderr)
        return 2
    args.artifact_output_root.mkdir(parents=True, exist_ok=True)
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
        except (json.JSONDecodeError, RecursionError) as exc:
            print(f"invalid adapter request line: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(evaluate(request, args, version), ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
