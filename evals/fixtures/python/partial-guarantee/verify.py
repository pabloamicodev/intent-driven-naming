import ast
import importlib.util
import sys
from pathlib import Path

candidate = Path(sys.argv[1])
source = candidate.read_text(encoding="utf-8")
tree = ast.parse(source)
names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
assert "validated_user" not in names
assert "user_for_authorization" in names

spec = importlib.util.spec_from_file_location("candidate_partial_guarantee", candidate)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

observed = []


def validate(user):
    observed.append(("validate", user))
    return {**user, "validated": True}


def authorize(user):
    observed.append(("authorize", user))
    return user


raw_user = {"id": "user-7"}
assert module.authorize_user(raw_user, False, validate, authorize) is raw_user
assert observed == [("authorize", raw_user)]

observed.clear()
validated_user = module.authorize_user(raw_user, True, validate, authorize)
assert validated_user == {"id": "user-7", "validated": True}
assert observed == [
    ("validate", raw_user),
    ("authorize", {"id": "user-7", "validated": True}),
]
