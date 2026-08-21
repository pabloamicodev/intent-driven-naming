import re
import sys
from pathlib import Path


configuration = Path(sys.argv[1]).read_text(encoding="utf-8")
assert re.search(r"resource\s+\"aws_s3_bucket\"\s+\"customer_exports\"", configuration)
assert re.search(r"moved\s*\{[^}]*from\s*=\s*aws_s3_bucket\.data", configuration, re.DOTALL)
assert re.search(r"to\s*=\s*aws_s3_bucket\.customer_exports", configuration)
assert 'bucket = "customer-exports-production"' in configuration
assert "aws_s3_bucket.customer_exports.arn" in configuration
