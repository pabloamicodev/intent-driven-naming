import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


candidate = Path(sys.argv[1]).resolve()
typescript_compiler = shutil.which("tsc")
assert typescript_compiler is not None
source = candidate.read_text(encoding="utf-8")
assert "amount_in_cents" in source
assert "totalInvoiceCents" in source
assert "function calc" not in source

with tempfile.TemporaryDirectory() as temporary_directory:
    output = Path(temporary_directory)
    subprocess.run(
        [
            typescript_compiler, str(candidate), "--strict", "--target", "ES2020",
            "--module", "commonjs", "--outDir", str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    module_path = output / (candidate.stem + ".js")
    probe = (
        "const m=require(" + json.dumps(str(module_path)) + ");"
        "if(m.totalInvoiceCents([{amount_in_cents:1200},{amount_in_cents:300}])!==1500)"
        "process.exit(1);"
    )
    subprocess.run(["node", "-e", probe], check=True)
