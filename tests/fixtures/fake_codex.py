import json
import sys
from pathlib import Path

if "--version" in sys.argv:
    print("codex-cli fake-1.0")
    raise SystemExit(0)

workspace = Path(sys.argv[sys.argv.index("--cd") + 1])
output = Path(sys.argv[sys.argv.index("--output-last-message") + 1])
used_skill = (workspace / ".agents" / "skills" / "intent-driven-naming" / "SKILL.md").is_file()
payload = {
    "selected_skill": used_skill,
    "loaded_resources": ["SKILL.md", "references/naming-model.md"] if used_skill else [],
    "answer": "fake isolated answer",
}
output.write_text(json.dumps(payload), encoding="utf-8")
print(json.dumps({"usage": {"input_tokens": 7, "output_tokens": 3}}))
