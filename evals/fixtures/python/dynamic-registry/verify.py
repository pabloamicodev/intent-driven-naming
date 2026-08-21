import importlib.util
import sys
from pathlib import Path


candidate = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("candidate_registry", candidate)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert set(module.handlers) == {"payment.succeeded"}
handler = module.handlers["payment.succeeded"]
assert handler.__name__ == "handle_payment_succeeded"
assert handler({"payment_id": "pay-123"}) == "pay-123"
