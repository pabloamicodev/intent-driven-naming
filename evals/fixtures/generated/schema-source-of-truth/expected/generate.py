import json
from pathlib import Path

root = Path(__file__).parent
schema = json.loads((root / "schema.json").read_text(encoding="utf-8"))
property_name = schema["typescript_property"]
(root / "generated_client.ts").write_text(
    "// generated; do not edit\n"
    "export function readCustomerId(payload: Record<string, string>): string {\n"
    f"  const {property_name} = payload[{schema['wire_key']!r}];\n"
    f"  return {property_name};\n}}\n",
    encoding="utf-8",
)
