import shutil
import subprocess
import sys
from pathlib import Path

candidate = Path(sys.argv[1])
source = candidate.read_text(encoding="utf-8")
for spelling in (
    "customer_id",
    "created_at_ms",
    "customerId",
    "createdAtEpochMs",
    "mapGeneratedCustomerToApplication",
):
    assert spelling in source
typescript_compiler = shutil.which("tsc")
assert typescript_compiler is not None
subprocess.run(
    [typescript_compiler, "--noEmit", "--strict", "--target", "ES2022", str(candidate)],
    capture_output=True,
    text=True,
    check=True,
)
