import json
import sys


for line in sys.stdin:
    request = json.loads(line)
    case = request["case"]
    response = {
        "protocol_version": 1,
        "case_id": case["id"],
        "status": "completed",
        "selected_skill": case.get("expected_activation"),
        "output_text": "mock output",
        "artifact_path": None,
        "usage": {
            "input_tokens": 1,
            "output_tokens": 1,
            "latency_ms": 1,
            "cost_usd": 0,
        },
        "implementation": {"adapter": "mock"},
        "error": None,
    }
    print(json.dumps(response))
