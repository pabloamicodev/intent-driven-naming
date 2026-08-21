import json
import sys


for line in sys.stdin:
    request = json.loads(line)
    print(
        json.dumps(
            {
                "protocol_version": 1,
                "run_id": "spoofed-run",
                "case_id": request["case"]["id"],
                "variant": request["variant"],
                "status": "completed",
                "selected_skill": True,
                "output_text": "spoofed",
            }
        )
    )
