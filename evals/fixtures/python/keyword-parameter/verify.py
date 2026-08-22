import importlib.util
import inspect
import sys
from pathlib import Path

candidate_path = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("candidate", candidate_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

signature = inspect.signature(module.summarize_invoices)
assert "id" in signature.parameters
assert module.summarize_invoices(
    id="customer-1",
    invoices=[
        {"customer_id": "customer-1", "amount_in_cents": 1200},
        {"customer_id": "customer-2", "amount_in_cents": 400},
        {"customer_id": "customer-1", "amount_in_cents": 300},
    ],
) == 1500
