import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


candidate = Path(sys.argv[1])
source = candidate.read_text(encoding="utf-8")
assert "String get(String id)" in source
assert "normalizeCustomerId" in source

with tempfile.TemporaryDirectory() as temporary_directory:
    workdir = Path(temporary_directory)
    implementation = workdir / "Implementation.java"
    shutil.copyfile(candidate, implementation)
    subprocess.run(["javac", str(implementation)], cwd=workdir, check=True)
    subprocess.run(["java", "-cp", str(workdir), "Implementation"], cwd=workdir, check=True)
