###############################################################################
# IAM
###############################################################################
data "aws_iam_policy_document" "search_role_policy" {
  version = "2012-10-17"
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "rekognition:DescribeCollection",
      "rekognition:SearchFacesByImage",
      "dynamodb:GetItem",
    ]
    resources = [
      "arn:aws:logs:*:*:*",
      "arn:aws:rekognition:*:*:collection/${local.collection_id}",
      "arn:aws:dynamodb:*:*:table/${local.table_name}"
    ]
  }
}

resource "aws_iam_role" "search_function" {
  name               = "faces-search-function-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.search_role_policy.json
}

resource "aws_iam_role_policy" "search_function" {
  name   = "cloudwatch_search"
  role   = aws_iam_role.search_function.id
  policy = data.aws_iam_policy_document.search_role_policy.json
}

###############################################################################
# Lambda
###############################################################################
# see https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file
data "archive_file" "lambda_search" {
  type        = "zip"
  source_file = "${path.module}/python/lambda_search.py"
  output_path = "${path.module}/python/lambda_search_function_payload.zip"
}


resource "aws_lambda_function" "search_function" {

  function_name = "personnel-recognition-searcher"
  role          = aws_iam_role.search_function.arn
  publish       = true
  runtime       = "python3.8"
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
