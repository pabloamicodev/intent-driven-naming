import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

candidate = Path(sys.argv[1]).resolve()
typescript_compiler = shutil.which("tsc")
assert typescript_compiler is not None
assert candidate.is_dir()
for required in ("schema.json", "generate.py", "generated_client.ts"):
    assert (candidate / required).is_file()
with tempfile.TemporaryDirectory() as temporary_directory:
    worktree = Path(temporary_directory) / "candidate"
    shutil.copytree(candidate, worktree)
    before = (worktree / "generated_client.ts").read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(worktree / "generate.py")], check=True)
    after = (worktree / "generated_client.ts").read_text(encoding="utf-8")
    assert before == after, "generated output is stale"
    assert "customer_id" in after
    assert "customerId" in after
    assert "const value" not in after
    subprocess.run(
        [typescript_compiler, str(worktree / "generated_client.ts"), "--strict", "--noEmit", "--target", "ES2020"],
        check=True,
        capture_output=True,
        text=True,
    )
