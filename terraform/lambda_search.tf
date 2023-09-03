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
      MAX_FACES_COUNT = var.max_faces_count
      FACE_DETECT_THRESHOLD = var.face_detect_threshold
      COLLECTION_ID = local.collection_id
      TABLE_ID = local.table_name
    }
  }
}
