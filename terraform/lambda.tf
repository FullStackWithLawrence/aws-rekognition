locals {
  lambda_role_name   = "${var.shared_resource_identifier}-lambda"
  lambda_policy_name = "${var.shared_resource_identifier}-lambda"
  iam_policy_lambda = templatefile("${path.module}/json/iam_policy_lambda.json.tpl", {
    s3_bucket_arn      = module.s3_bucket.s3_bucket_arn
    dynamodb_table_arn = module.dynamodb_table.dynamodb_table_arn
  })
}

resource "aws_iam_role" "lambda" {
  name               = local.lambda_role_name
  assume_role_policy = file("${path.module}/json/iam_role_lambda.json")
  tags               = var.tags
}

resource "aws_iam_policy" "lambda" {
  name        = local.lambda_policy_name
  description = "generic IAM policy"
  policy      = local.iam_policy_lambda
}


resource "aws_iam_role_policy_attachment" "lambda" {
  role       = aws_iam_role.lambda.id
  policy_arn = aws_iam_policy.lambda.arn
}

# ----------------------------------------------------------------------
# FIX NOTE: these permissions are too broad.
# ----------------------------------------------------------------------
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

resource "aws_iam_role_policy_attachment" "AmazonDynamoDBFullAccess" {
  role       = aws_iam_role.lambda.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}
resource "aws_iam_role_policy_attachment" "AmazonRekognitionFullAccess" {
  role       = aws_iam_role.lambda.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonRekognitionFullAccess"
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
