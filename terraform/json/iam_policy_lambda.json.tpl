{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["${s3_bucket_arn}/*"]
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem"],
      "Resource": [
        "${dynamodb_table_arn}/*"
      ]
    },
    {
        "Effect": "Allow",
        "Action": [
          "apigateway:GET",
          "iam:ListPolicies",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListAttachedRolePolicies",
          "s3:ListAllMyBuckets",
          "rekognition:IndexFaces",
          "rekognition:DescribeCollection",
          "ec2:DescribeRegions",
          "route53:ListHostedZones",
          "route53:ListResourceRecordSets"
        ],
        "Resource": "*"
    }
  ]
}
