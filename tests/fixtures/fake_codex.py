import json
import sys
from pathlib import Path

# Fix stdin/stdout to UTF-8 regardless of the host's default locale encoding,
# so this fixture behaves like the real Codex CLI and isolates encoding bugs
# to the code under test (adapters/codex_cli.py's own subprocess calls)
# instead of the fixture's own I/O.
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

if "--version" in sys.argv:
    print("codex-cli fake-1.0")
    raise SystemExit(0)

workspace = Path(sys.argv[sys.argv.index("--cd") + 1])
output = Path(sys.argv[sys.argv.index("--output-last-message") + 1])
used_skill = (workspace / ".agents" / "skills" / "intent-driven-naming" / "SKILL.md").is_file()
# Echo the received prompt verbatim so tests can assert non-ASCII stdin
# survives the adapter's subprocess boundary without mojibake.
received_prompt = sys.stdin.read()
payload = {
    "selected_skill": used_skill,
    "loaded_resources": ["SKILL.md", "references/naming-model.md"] if used_skill else [],
    "answer": received_prompt or "fake isolated answer",
}
output.write_text(json.dumps(payload), encoding="utf-8")
print(json.dumps({"usage": {"input_tokens": 7, "output_tokens": 3}}))
