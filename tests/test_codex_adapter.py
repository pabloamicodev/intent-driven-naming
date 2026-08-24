import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.eval_core import read_jsonl

ROOT = Path(__file__).resolve().parents[1]


class CodexAdapterTest(unittest.TestCase):
    def test_reference_adapter_isolates_and_reports_runtime_skill(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            records_by_variant = {}
            for variant in ("with-skill", "previous-skill", "without-skill"):
                output = temporary / f"{variant}.jsonl"
                command = [
                    sys.executable, str(ROOT / "harness" / "run_adapter.py"),
                    "--cases", str(ROOT / "evals" / "cases" / "activation.jsonl"),
                    "--output", str(output), "--variant", variant,
                    "--system-id", "fake-codex", "--limit", "1",
                ]
                if variant == "previous-skill":
                    command.extend(["--baseline-skill-path", str(ROOT)])
                command.extend([
                    "--",
                    sys.executable, str(ROOT / "adapters" / "codex_cli.py"),
                    "--codex", sys.executable,
                    "--codex-prefix-arg", str(ROOT / "tests" / "fixtures" / "fake_codex.py"),
                    "--model", "fake-model", "--model-version", "fake-version",
                    "--artifact-output-root", str(temporary / "artifacts"),
                ])
                subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
                records_by_variant[variant] = read_jsonl(output)[0]
            self.assertTrue(records_by_variant["with-skill"]["selected_skill"])
            self.assertFalse(records_by_variant["without-skill"]["selected_skill"])
            self.assertTrue(records_by_variant["previous-skill"]["selected_skill"])
            self.assertEqual(records_by_variant["without-skill"]["loaded_resources"], [])
            self.assertEqual(records_by_variant["with-skill"]["implementation"]["agent"], "codex-cli")
            self.assertIn(
                "references/naming-model.md",
                records_by_variant["with-skill"]["loaded_resources"],
            )
            self.assertGreater(
                records_by_variant["with-skill"]["usage"]["skill_context_words"], 0
            )

    def test_rejects_reasoning_value_that_would_break_config_quoting(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            completed = subprocess.run(
                [
                    sys.executable, str(ROOT / "adapters" / "codex_cli.py"),
                    "--model", "fake-model", "--model-version", "fake-version",
                    "--reasoning", 'high" extra_key="injected',
                    "--artifact-output-root", str(Path(temporary_directory) / "artifacts"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("--reasoning must match", completed.stderr)

    def test_preserves_non_ascii_prompt_across_the_subprocess_boundary(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            spanish_prompt = (
                "¿Podés revisar la función de validación de contraseñas? "
                "Necesito nombres más claros para las variables temporales."
            )
            case = {
                "schema_version": "1.0",
                "dataset_version": "test-1.0",
                "id": "T99",
                "suite": "activation",
                "title": "Caso en español",
                "prompt": spanish_prompt,
                "difficulty": "standard",
                "locale": "es",
                "tags": ["activation"],
                "expected_activation": True,
                "rationale": "Tarea de nomenclatura de identificadores.",
            }
            cases_path = temporary / "activation.jsonl"
            cases_path.write_text(json.dumps(case) + "\n", encoding="utf-8")
            output = temporary / "with-skill.jsonl"
            command = [
                sys.executable, str(ROOT / "harness" / "run_adapter.py"),
                "--cases", str(cases_path),
                "--output", str(output), "--variant", "with-skill",
                "--system-id", "fake-codex", "--limit", "1",
                "--",
                sys.executable, str(ROOT / "adapters" / "codex_cli.py"),
                "--codex", sys.executable,
                "--codex-prefix-arg", str(ROOT / "tests" / "fixtures" / "fake_codex.py"),
                "--model", "fake-model", "--model-version", "fake-version",
                "--artifact-output-root", str(temporary / "artifacts"),
            ]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            result = read_jsonl(output)[0]
            self.assertIn(spanish_prompt, result["output_text"])


if __name__ == "__main__":
    unittest.main()
