#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: sep-2023
#
# usage:  - implement a Python Lambda function to search the Rekognition index
#           for an image uploaded using the REST API endpoint.
#------------------------------------------------------------------------------
locals {
  index_function_name = "${var.shared_resource_identifier}-index"
}

# see https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file
data "archive_file" "lambda_index" {
  type        = "zip"
  source_file = "${path.module}/python/lambda_index.py"
  output_path = "${path.module}/python/lambda_index_payload.zip"
}

# see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function.html
resource "aws_lambda_function" "index" {

  # see https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
  function_name = local.index_function_name
  description   = "Facial recognition analysis and indexing of images. Invoked by S3."
  role          = aws_iam_role.lambda.arn
  publish       = true
  runtime       = var.lambda_python_runtime
  memory_size   = var.lambda_memory_size
  timeout       = var.lambda_timeout
  handler       = "lambda_index.lambda_handler"

  filename         = data.archive_file.lambda_index.output_path
  source_code_hash = data.archive_file.lambda_index.output_base64sha256
  tags             = var.tags

  environment {
    variables = {
      DEBUG_MODE             = var.debug_mode
      COLLECTION_ID          = local.collection_id
      TABLE_ID               = local.table_name
      MAX_FACES_COUNT        = var.max_faces_count
      S3_BUCKET_NAME         = module.s3_bucket.s3_bucket_id
      FACE_DETECT_ATTRIBUTES = var.face_detect_attributes
      QUALITY_FILTER         = var.face_detect_quality_filter
    }
  }
}

resource "aws_lambda_permission" "s3_permission_to_trigger_lambda" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.index.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.s3_bucket.s3_bucket_arn
}

# see https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/r/s3_bucket_notification.html.markdown
resource "aws_s3_bucket_notification" "incoming_jpg" {
  bucket = module.s3_bucket.s3_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.index.arn
    events              = ["s3:ObjectCreated:*"]
    #filter_prefix       = ""
    filter_suffix = ".jpg"
  }

  depends_on = [
    aws_lambda_permission.s3_permission_to_trigger_lambda
  ]
}

###############################################################################
# Cloudwatch logging
###############################################################################
resource "aws_cloudwatch_log_group" "index" {
  name              = "/aws/lambda/${local.index_function_name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}
