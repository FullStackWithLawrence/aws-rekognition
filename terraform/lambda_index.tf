###############################################################################
# Lambda
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
      COLLECTION_ID = local.collection_id
      TABLE_ID = local.table_name
    }
  }
}
