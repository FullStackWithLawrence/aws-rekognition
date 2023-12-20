#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: sep-2023
#
# usage:  - implement a Python Lambda function to create a dump of the
#           configuration settings for the facial recognition system.
#------------------------------------------------------------------------------
locals {
  info_function_name = "${var.shared_resource_identifier}_info"
}

resource "aws_lambda_function" "info" {

  # see https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
  function_name    = local.info_function_name
  description      = "Facial recognition configuration settings. invoked by API Gateway."
  role             = aws_iam_role.lambda.arn
  publish          = true
  runtime          = var.lambda_python_runtime
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout
  handler          = "rekognition_api.lambda_info.lambda_handler"
  filename         = data.archive_file.lambda_info.output_path
  source_code_hash = data.archive_file.lambda_info.output_base64sha256
  layers           = [aws_lambda_layer_version.rekognition.arn]
  tags             = var.tags

  environment {
    variables = {
      DEBUG_MODE                             = var.debug_mode
      MAX_FACES_COUNT                        = var.aws_rekognition_max_faces_count
      AWS_REKOGNITION_FACE_DETECT_THRESHOLD  = var.aws_rekognition_face_detect_threshold
      QUALITY_FILTER                         = var.aws_rekognition_face_detect_quality_filter
      AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES = var.aws_rekognition_face_detect_attributes
      AWS_DYNAMODB_TABLE_ID                  = local.table_name
      AWS_DEPLOYED                           = true
      AWS_REKOGNITION_COLLECTION_ID          = local.aws_rekognition_collection_id
    }
  }
}

###############################################################################
# Cloudwatch logging
###############################################################################
resource "aws_cloudwatch_log_group" "info" {
  name              = "/aws/lambda/${local.info_function_name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}


###############################################################################
# Lambda Search
###############################################################################

# see https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file
data "archive_file" "lambda_info" {
  type        = "zip"
  source_dir  = "${path.module}/build/python/"
  output_path = "${path.module}/build/lambda_info_payload.zip"

  depends_on = [null_resource.build_lambda_index]
}
