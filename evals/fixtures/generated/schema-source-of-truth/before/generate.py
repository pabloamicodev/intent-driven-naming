import json
from pathlib import Path

root = Path(__file__).parent
schema = json.loads((root / "schema.json").read_text(encoding="utf-8"))
(root / "generated_client.ts").write_text(
    "// generated; do not edit\n"
    "export function readCustomerId(payload: Record<string, string>): string {\n"
    f"  const value = payload[{schema['wire_key']!r}];\n"
    "  return value;\n}\n",
    encoding="utf-8",
)
