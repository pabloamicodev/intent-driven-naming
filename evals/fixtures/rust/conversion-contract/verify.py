import subprocess
import sys
import tempfile
from pathlib import Path

candidate = Path(sys.argv[1])
source = candidate.read_text(encoding="utf-8")
assert "fn into_order(self)" in source
assert ".clone()" not in source

with tempfile.TemporaryDirectory() as temporary_directory:
    binary = Path(temporary_directory) / ("fixture.exe" if sys.platform == "win32" else "fixture")
    subprocess.run(["rustc", str(candidate), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
