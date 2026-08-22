import subprocess
import sys
import tempfile
from pathlib import Path

candidate = Path(sys.argv[1]).resolve()
source = candidate.read_text(encoding="utf-8")
assert "Process(string id)" in source
assert "Process(id:" in source

with tempfile.TemporaryDirectory() as temporary_directory:
    project = Path(temporary_directory)
    (project / "Fixture.csproj").write_text(
        '<Project Sdk="Microsoft.NET.Sdk">'
        '<PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>'
        '<ImplicitUsings>disable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup>'
        '</Project>',
        encoding="utf-8",
    )
    (project / "Program.cs").write_text(source, encoding="utf-8")
    subprocess.run(
        ["dotnet", "build", str(project / "Fixture.csproj"), "--nologo", "--verbosity", "quiet"],
        check=True,
        capture_output=True,
        text=True,
    )
    completed = subprocess.run(
        ["dotnet", "run", "--project", str(project / "Fixture.csproj"), "--no-build"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout == "pay-123"
