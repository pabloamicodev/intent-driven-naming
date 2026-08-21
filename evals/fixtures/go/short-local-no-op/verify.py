import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


candidate = Path(sys.argv[1]).read_text(encoding="utf-8").replace("\r\n", "\n")
expected = Path("expected.go").read_text(encoding="utf-8").replace("\r\n", "\n")
assert candidate == expected, "the no-op fixture must remain byte-equivalent after newline normalization"

with tempfile.TemporaryDirectory() as temporary_directory:
    workdir = Path(temporary_directory)
    shutil.copyfile(sys.argv[1], workdir / "sum.go")
    (workdir / "go.mod").write_text("module fixture\n\ngo 1.22\n", encoding="utf-8")
    (workdir / "sum_test.go").write_text(
        "package sum\n\nimport \"testing\"\n\n"
        "func TestSum(t *testing.T) {\n"
        "\tif Sum([]int{1, 2, 3}) != 6 { t.Fatal(\"unexpected sum\") }\n"
        "}\n",
        encoding="utf-8",
    )
    subprocess.run(["go", "test", "./..."], cwd=workdir, check=True)
