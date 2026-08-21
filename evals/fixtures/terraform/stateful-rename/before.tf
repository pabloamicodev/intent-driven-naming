resource "aws_s3_bucket" "data" {
  bucket = "customer-exports-production"
}

output "exports_bucket_arn" {
  value = aws_s3_bucket.data.arn
}
