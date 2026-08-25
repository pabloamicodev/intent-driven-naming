"""Load the skill's bundled validate_rename_plan module by file path.

skills/intent-driven-naming/ cannot be a dotted Python package (the
hyphenated directory name is not a valid identifier), so the module is
loaded directly from its file location instead of via `import`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

_ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = (
    _ROOT / "skills" / "intent-driven-naming" / "scripts" / "runtime" / "validate_rename_plan.py"
)


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "intent_driven_naming_validate_rename_plan", _MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_rename_plan = _load()
