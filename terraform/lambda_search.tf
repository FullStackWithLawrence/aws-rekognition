#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: sep-2023
#
# usage:  - implement a Python Lambda function to create a 'faceprint' of an image
#           triggered by uploading the image to the S3 bucket
#
#         - implement a Python Lambda function to search the Rekognition index
#           for an image uploaded using the REST API endpoint.
#
#         - implement role-based security for both Lambda functions.
#------------------------------------------------------------------------------

###############################################################################
# Lambda IAM
###############################################################################
resource "aws_iam_role" "facialrecognition" {
  name               = "${var.shared_resource_identifier}-iam-role"
  assume_role_policy = file("${path.module}/json/iam_role_lambda.json")
}

data "template_file" "iam_policy_lambda" {
  template = file("${path.module}/json/iam_policy_lambda.json.tpl")
  vars = {
    s3_bucket_arn      = module.s3_bucket.s3_bucket_arn
    dynamodb_table_arn = module.dynamodb_table.dynamodb_table_arn
  }
}
resource "aws_iam_policy" "facialrecognition" {
  name        = "${var.shared_resource_identifier}-iam-policy"
  description = "generic IAM policy"
  policy      = data.template_file.iam_policy_lambda.rendered
}


resource "aws_iam_role_policy_attachment" "facialrecognition" {
  role       = aws_iam_role.facialrecognition.id
  policy_arn = "arn:aws:iam::${var.aws_account_id}:policy/${var.shared_resource_identifier}-iam-policy"
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
  function_name = "${var.shared_resource_identifier}-search"
  role          = aws_iam_role.facialrecognition.arn
  publish       = true
  runtime       = "python3.11"
  handler       = "search.lambda_handler"
  memory_size   = 512
  timeout       = 60

  filename         = data.archive_file.lambda_search.output_path
  source_code_hash = data.archive_file.lambda_search.output_base64sha256

  environment {
    variables = {
      MAX_FACES_COUNT       = var.max_faces_count
      FACE_DETECT_THRESHOLD = var.face_detect_threshold
      COLLECTION_ID         = local.collection_id
      TABLE_ID              = local.table_name
    }
  }
}
