#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: Feb-2022
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
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "lambda.amazonaws.com",
          "rekognition.amazonaws.com",
          "dynamodb.amazonaws.com",
          "apigateway.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "facialrecognition" {
  name        = "${var.shared_resource_identifier}-iam-policy"
  description = "generic IAM policy"
  policy      = file("${path.module}/json/policy.json")
}


resource "aws_iam_role_policy_attachment" "facialrecognition" {
  role       = aws_iam_role.facialrecognition.id
  policy_arn = "arn:aws:iam::${var.aws_account_id}:policy/${var.shared_resource_identifier}-iam-policy"
}


###############################################################################
# Lambda Index
###############################################################################
# see https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file
data "archive_file" "lambda_index" {
  type        = "zip"
  source_file = "${path.module}/python/lambda_index.py"
  output_path = "${path.module}/python/lambda_index_function_payload.zip"
}

resource "aws_lambda_permission" "s3_permission_to_trigger_lambda" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.index_function.arn
  principal     = "s3.amazonaws.com"
  source_arn    = module.personnel_bucket.s3_bucket_arn
}

resource "aws_s3_bucket_notification" "incoming" {
  bucket = module.personnel_bucket.s3_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.index_function.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "photos/portrait"
    filter_suffix       = ".jpg"
  }

  depends_on = [aws_lambda_permission.s3_permission_to_trigger_lambda]
}

# see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function.html
resource "aws_lambda_function" "index_function" {

  # see https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
  function_name = "${var.shared_resource_identifier}-index"
  role          = aws_iam_role.facialrecognition.arn
  publish       = true
  runtime       = "python3.11"
  handler       = "search_function.lambda_handler"
  memory_size   = 512
  timeout       = 60

  filename         = data.archive_file.lambda_index.output_path
  source_code_hash = data.archive_file.lambda_index.output_base64sha256

  environment {
    variables = {
      COLLECTION_ID   = local.collection_id
      TABLE_ID        = local.table_name
      MAX_FACES_COUNT = var.max_faces_count
    }
  }
}

###############################################################################
# Lambda Search
###############################################################################
# see https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file
data "archive_file" "lambda_search" {
  type        = "zip"
  source_file = "${path.module}/python/lambda_search.py"
  output_path = "${path.module}/python/lambda_search_function_payload.zip"
}


resource "aws_lambda_function" "search_function" {

  # see https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
  function_name = "${var.shared_resource_identifier}-search"
  role          = aws_iam_role.facialrecognition.arn
  publish       = true
  runtime       = "python3.11"
  handler       = "search_function.lambda_handler"
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
