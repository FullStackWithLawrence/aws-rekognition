#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: sep-2023
#
# usage:  implement a Python Lambda function to search the Rekognition index
#         for an image uploaded using the REST API endpoint.
#------------------------------------------------------------------------------
locals {
  index_function_name = "${var.shared_resource_identifier}_index"
}

resource "aws_lambda_function" "index" {
  # see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function.html
  # see https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
  function_name    = local.index_function_name
  description      = "Facial recognition analysis and indexing of images. Invoked by S3."
  role             = aws_iam_role.lambda.arn
  publish          = true
  runtime          = var.lambda_python_runtime
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout
  handler          = "rekognition_api.lambda_index.lambda_handler"
  filename         = data.archive_file.lambda_index.output_path
  source_code_hash = data.archive_file.lambda_index.output_base64sha256
  layers           = [aws_lambda_layer_version.rekognition.arn]
  tags             = var.tags

  environment {
    variables = {
      DEBUG_MODE                             = var.debug_mode
      AWS_REKOGNITION_COLLECTION_ID          = local.aws_rekognition_collection_id
      AWS_DYNAMODB_TABLE_ID                  = local.table_name
      MAX_FACES_COUNT                        = var.aws_rekognition_max_faces_count
      S3_BUCKET_NAME                         = module.s3_bucket.s3_bucket_id
      AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES = var.aws_rekognition_face_detect_attributes
      QUALITY_FILTER                         = var.aws_rekognition_face_detect_quality_filter
    }
  }
}

# ------------------------------------------------------------------
# note: this preps the Python code for deployment to Lambda
# for both lambdas. we need to do this because the Python code
# is in a subdirectory of the terraform project.
# ------------------------------------------------------------------
resource "null_resource" "build_lambda_index" {
  triggers = {
    always_run = "${timestamp()}"
  }

  provisioner "local-exec" {
    command = "rm -rf ${path.module}/build/*.zip; rm -rf ${path.module}/build/python; mkdir -p ${path.module}/build/python/rekognition_api; cp ${path.module}/python/rekognition_api/*.py ${path.module}/build/python/rekognition_api"
  }
}

# see https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file
data "archive_file" "lambda_index" {
  type        = "zip"
  source_dir  = "${path.module}/build/python/"
  output_path = "${path.module}/build/lambda_index_payload.zip"

  depends_on = [null_resource.build_lambda_index]
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
    filter_suffix       = ".jpg"
    #filter_prefix       = ""
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
