resource "aws_iam_role" "facialrecognition" {
  name = "${var.shared_resource_identifier}-iam-role"
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
  name = "${var.shared_resource_identifier}-iam-policy"
  description = "generic IAM policy"
  policy = file("${path.module}/json/policy.json")
}


resource "aws_iam_role_policy_attachment" "facialrecognition" {
  role   = aws_iam_role.facialrecognition.id
  policy_arn = "arn:aws:iam::${var.aws_account_id}:policy/${var.shared_resource_identifier}-iam-policy"
}

