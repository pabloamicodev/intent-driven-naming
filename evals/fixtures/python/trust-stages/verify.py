import ast
import importlib.util
import sys
from pathlib import Path

candidate = Path(sys.argv[1])
source = candidate.read_text(encoding="utf-8")
tree = ast.parse(source)
names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
assert {"untrusted_authorization_header", "untrusted_token", "verified_token_claims"} <= names
spec = importlib.util.spec_from_file_location("candidate_trust", candidate)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
observed = []


def verify_token(token):
    observed.append(token)
    return {"sub": "principal-7"}


assert module.authenticate_authorization_header("Bearer token-1", verify_token) == {
    "principal_id": "principal-7"
}
assert observed == ["token-1"]
