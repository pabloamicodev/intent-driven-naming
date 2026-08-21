moved {
  from = aws_s3_bucket.data
  to   = aws_s3_bucket.customer_exports
}

resource "aws_s3_bucket" "customer_exports" {
  bucket = "customer-exports-production"
}

output "exports_bucket_arn" {
  value = aws_s3_bucket.customer_exports.arn
}
