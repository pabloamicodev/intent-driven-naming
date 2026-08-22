import shutil
import subprocess
import sys
from pathlib import Path

candidate = Path(sys.argv[1])
source = candidate.read_text(encoding="utf-8")
assert "deploy_to_environment()" in source
assert 'DEPLOY_ENV="$deployment_environment"' in source
assert 'run_deploy "$dry_run_flag"' in source
bash = shutil.which("bash")
assert bash is not None
probe = source + """
run_deploy() { printf '%s|%s' "$DEPLOY_ENV" "$1"; return 7; }
output=$(deploy_to_environment 'staging west' '--dry-run')
status=$?
printf '%s\n%s' "$output" "$status"
"""
completed = subprocess.run(
    [bash], input=probe.encode("utf-8"), capture_output=True, check=False
)
stderr = completed.stderr.decode("utf-8")
stdout = completed.stdout.decode("utf-8")
assert completed.returncode == 0, stderr
assert not stderr, stderr
assert stdout.splitlines() == ["staging west|--dry-run", "7"], repr(stdout)
