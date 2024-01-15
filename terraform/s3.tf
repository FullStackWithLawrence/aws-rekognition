resource "random_id" "hash" {
  byte_length = 16
}

module "s3_bucket" {
  # see https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 4.0"

  bucket                   = "${var.aws_account_id}-${var.shared_resource_identifier}-${random_id.hash.hex}"
  acl                      = "private"
  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  cors_rule = [
    {
      allowed_methods = ["GET", "POST", "PUT", "HEAD"]
      allowed_origins = [
        "https://${local.api_gateway_subdomain}",
        "http://${local.api_gateway_subdomain}"
      ]
      allowed_headers = ["*"]
      expose_headers = [
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Method",
        "Access-Control-Allow-Header"
      ]
      max_age_seconds = 3000
    }
  ]
  versioning = {
    enabled = false
  }
  tags = var.tags
}
