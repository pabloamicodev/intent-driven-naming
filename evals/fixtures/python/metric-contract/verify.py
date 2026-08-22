import importlib.util
import inspect
import sys
from pathlib import Path

candidate = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("candidate_metric", candidate)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
metric_name, labels, increment = module.build_checkout_attempt_metric("success", "card")
assert metric_name == "checkout_attempts_total"
assert labels == {"result": "success", "payment_method": "card"}
assert increment == 1
source = inspect.getsource(module.build_checkout_attempt_metric)
assert "customer_id" not in source
