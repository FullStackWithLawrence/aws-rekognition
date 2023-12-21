#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: sep-2023
#
# usage:  - implement a REST API with a single end point for posting an image.
#         - add a DNS record for the REST API
#         - add TLS/SSL termination for https
#
# see:    https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_model.html
#         https://developer.hashicorp.com/terraform/tutorials/aws/lambda-api-gateway
#------------------------------------------------------------------------------
locals {
  api_gateway_subdomain    = "api.${var.shared_resource_identifier}.${var.aws_apigateway_root_domain}"
  api_name                 = "${var.shared_resource_identifier}-api"
  apigateway_iam_role_name = "${var.shared_resource_identifier}-apigateway"
  iam_role_policy_name     = "${var.shared_resource_identifier}-apigateway"
  iam_policy_apigateway = templatefile("${path.module}/json/iam_policy_apigateway.json.tpl", {
    aws_account_id = data.aws_caller_identity.current.account_id
    bucket_name    = module.s3_bucket.s3_bucket_id
  })
}

# WARNING: You need a pre-existing Route53 Hosted Zone
# for aws_apigateway_root_domain located in your AWS account.
# see: https://aws.amazon.com/route53/
data "aws_route53_zone" "aws_apigateway_root_domain" {
  name = var.aws_apigateway_root_domain
}

data "aws_caller_identity" "current" {}

###############################################################################
# Top-level REST API resources
###############################################################################

# see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_rest_api
resource "aws_api_gateway_rest_api" "rekognition" {
  name        = local.api_name
  description = "Facial recognition micro service"

  # Note: our api is used exclusively to upload images file, hence
  # we want ALL requests to be treated as 'binary'. An example
  # alternative to this might be, say, 'image/jpeg', 'image/png', etc.
  binary_media_types = [
    "*/*"
  ]
  api_key_source = "HEADER"
  endpoint_configuration {
    types = ["EDGE"]
  }
  tags = var.tags
}
resource "aws_api_gateway_api_key" "rekognition" {
  name = var.shared_resource_identifier
  tags = var.tags
}


resource "aws_api_gateway_deployment" "rekognition" {
  rest_api_id = aws_api_gateway_rest_api.rekognition.id
  depends_on = [
    aws_api_gateway_integration.index_put,
    aws_api_gateway_integration.search
  ]
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.rekognition.body,
      aws_api_gateway_integration.index_put.id,
      aws_api_gateway_integration.search.id
    ]))
  }
  lifecycle {
    create_before_destroy = true
  }
}
# see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_stage
resource "aws_api_gateway_stage" "rekognition" {
  deployment_id      = aws_api_gateway_deployment.rekognition.id
  cache_cluster_size = "0.5"
  rest_api_id        = aws_api_gateway_rest_api.rekognition.id
  stage_name         = var.stage
  tags               = var.tags
}

resource "aws_api_gateway_method_settings" "rekognition" {
  rest_api_id = aws_api_gateway_rest_api.rekognition.id
  stage_name  = aws_api_gateway_stage.rekognition.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled        = true
    data_trace_enabled     = true
    logging_level          = var.logging_level
    throttling_burst_limit = var.throttle_settings_burst_limit
    throttling_rate_limit  = var.throttle_settings_rate_limit
  }
}
resource "aws_api_gateway_usage_plan" "rekognition" {
  name        = var.shared_resource_identifier
  description = "Default usage plan"
  api_stages {
    api_id = aws_api_gateway_rest_api.rekognition.id
    stage  = aws_api_gateway_stage.rekognition.stage_name
  }
  quota_settings {
    limit  = var.quota_settings_limit
    offset = var.quota_settings_offset
    period = var.quota_settings_period
  }
  throttle_settings {
    burst_limit = var.throttle_settings_burst_limit
    rate_limit  = var.throttle_settings_rate_limit
  }
  tags = var.tags
}
resource "aws_api_gateway_usage_plan_key" "rekognition" {
  key_id        = aws_api_gateway_api_key.rekognition.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.rekognition.id
}


###############################################################################
# REST API resources - IAM
###############################################################################
resource "aws_iam_role" "apigateway" {
  name               = local.apigateway_iam_role_name
  description        = "Allows API Gateway to push files to an S3 bucket"
  assume_role_policy = file("${path.module}/json/iam_role_apigateway.json")
  tags               = var.tags
}
resource "aws_iam_role_policy_attachment" "cloudwatch_apigateway" {
  role       = aws_iam_role.apigateway.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}


resource "aws_iam_role_policy" "iam_policy_apigateway" {
  name   = local.iam_role_policy_name
  role   = aws_iam_role.apigateway.id
  policy = local.iam_policy_apigateway
}
