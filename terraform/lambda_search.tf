#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: sep-2023
#
# usage:  - implement a Python Lambda function to create a 'faceprint' of an image
#           triggered by uploading the image to the S3 bucket
#
#         - implement role-based security for both Lambda functions.
#------------------------------------------------------------------------------
locals {
  lambda_role_name     = "${var.shared_resource_identifier}-lambda"
  lambda_policy_name   = "${var.shared_resource_identifier}-lambda"
  search_function_name = "${var.shared_resource_identifier}-search"
}

resource "aws_iam_role" "lambda" {
  name               = local.lambda_role_name
  assume_role_policy = file("${path.module}/json/iam_role_lambda.json")
  tags               = var.tags
}

data "template_file" "iam_policy_lambda" {
  template = file("${path.module}/json/iam_policy_lambda.json.tpl")
  vars = {
    s3_bucket_arn      = module.s3_bucket.s3_bucket_arn
    dynamodb_table_arn = module.dynamodb_table.dynamodb_table_arn
  }
}
resource "aws_iam_policy" "lambda" {
  name        = local.lambda_policy_name
  description = "generic IAM policy"
  policy      = data.template_file.iam_policy_lambda.rendered
}


resource "aws_iam_role_policy_attachment" "lambda" {
  role       = aws_iam_role.lambda.id
  policy_arn = aws_iam_policy.lambda.arn
}

resource "aws_iam_role_policy_attachment" "lambda_AmazonS3FullAccess" {
  role       = aws_iam_role.lambda.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_CloudWatchFullAccess" {
  role       = aws_iam_role.lambda.id
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_AWSLambdaExecute" {
  role       = aws_iam_role.lambda.id
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = file("${path.module}/json/iam_policy_lambda_logging.json")
  tags        = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

###############################################################################
# Cloudwatch logging
###############################################################################
resource "aws_cloudwatch_log_group" "search" {
  name              = "/aws/lambda/${local.search_function_name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}


###############################################################################
# Lambda Search
###############################################################################
# see https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file
data "archive_file" "lambda_search" {
  type        = "zip"
  source_file = "${path.module}/python/lambda_search.py"
  output_path = "${path.module}/python/lambda_search_payload.zip"
}


resource "aws_lambda_function" "search" {

  # see https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
  function_name = local.search_function_name
  role          = aws_iam_role.lambda.arn
  publish       = true
  runtime       = var.lambda_python_runtime
  memory_size   = var.lambda_memory_size
  timeout       = var.lambda_timeout
  handler       = "lambda_search.lambda_handler"

  filename         = data.archive_file.lambda_search.output_path
  source_code_hash = data.archive_file.lambda_search.output_base64sha256

  environment {
    variables = {
      DEBUG_MODE             = var.debug_mode
      MAX_FACES_COUNT        = var.max_faces_count
      FACE_DETECT_THRESHOLD  = var.face_detect_threshold
      QUALITY_FILTER         = var.face_detect_quality_filter
      FACE_DETECT_ATTRIBUTES = var.face_detect_attributes
      TABLE_ID               = local.table_name
      REGION                 = var.aws_region
      COLLECTION_ID          = local.collection_id
    }
  }
}
