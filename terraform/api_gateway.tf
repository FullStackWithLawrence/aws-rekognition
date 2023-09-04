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
# see:    https://developer.hashicorp.com/terraform/tutorials/aws/lambda-api-gateway
#------------------------------------------------------------------------------
locals {
  api_gateway_subdomain = "api.${var.shared_resource_identifier}.${var.root_domain}"
  api_name              = "${var.shared_resource_identifier}-api"
  iam_role_name         = "${var.shared_resource_identifier}-apigateway"
  iam_role_policy_name  = "${var.shared_resource_identifier}-apigateway"
}

# WARNING: You need a pre-existing Route53 Hosted Zone
# for root_domain located in your AWS account.
# see: https://aws.amazon.com/route53/
data "aws_route53_zone" "root_domain" {
  name = var.root_domain
}

data "aws_caller_identity" "current" {}

###############################################################################
# Top-level REST API resources
###############################################################################
resource "aws_api_gateway_rest_api" "facialrecognition" {
  name = local.api_name
  tags = var.tags
}
resource "aws_api_gateway_api_key" "facialrecognition" {
  name = var.shared_resource_identifier
  tags = var.tags
}


resource "aws_api_gateway_deployment" "facialrecognition" {
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  depends_on = [
    aws_api_gateway_integration.index,
    aws_api_gateway_integration.search
  ]
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.facialrecognition.body,
      aws_api_gateway_integration.index.id,
      aws_api_gateway_integration.search.id
    ]))
  }
  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_api_gateway_stage" "facialrecognition" {
  deployment_id      = aws_api_gateway_deployment.facialrecognition.id
  cache_cluster_size = "0.5"
  rest_api_id        = aws_api_gateway_rest_api.facialrecognition.id
  stage_name         = var.stage
  tags               = var.tags
}
resource "aws_api_gateway_usage_plan" "facialrecognition" {
  name        = var.shared_resource_identifier
  description = "Default usage plan"
  api_stages {
    api_id = aws_api_gateway_rest_api.facialrecognition.id
    stage  = aws_api_gateway_stage.facialrecognition.stage_name
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
resource "aws_api_gateway_usage_plan_key" "facialrecognition" {
  key_id        = aws_api_gateway_api_key.facialrecognition.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.facialrecognition.id
}


###############################################################################
# REST API resources - IAM
###############################################################################
resource "aws_iam_role" "apigateway_s3_uploader" {
  name               = local.iam_role_name
  description        = "Allows API Gateway to push logs to CloudWatch Logs."
  assume_role_policy = file("${path.module}/json/iam_role_apigateway_s3_uploader.json")
  tags               = var.tags
}
resource "aws_iam_role_policy_attachment" "cloudwatch_apigateway" {
  role       = aws_iam_role.apigateway_s3_uploader.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}
data "template_file" "iam_policy_apigateway_s3_readwrite" {
  template = file("${path.module}/json/iam_policy_apigateway_s3_readwrite.json.tpl")
  vars = {
    aws_account_id = var.aws_account_id
    bucket_name    = module.s3_bucket.s3_bucket_id
  }
}

resource "aws_iam_role_policy" "iam_policy_apigateway_s3_readwrite" {
  name   = local.iam_role_policy_name
  role   = aws_iam_role.apigateway_s3_uploader.id
  policy = data.template_file.iam_policy_apigateway_s3_readwrite.rendered
}

###############################################################################
# REST API resources - index end point
# This is an HTTP Post request, to upload an image file to an AWS S3 bucket.
#
# workflow is: 1. method request        (from Postman, curl, your application, etc.)
#              2. integration request   (we're integrating to an AWS S3 bucket)
#              3. integration response
#              4. method response       (hopefully, an http 200 response)
#
# see https://medium.com/@ekantmate/webhook-for-s3-bucket-by-terraform-rest-api-in-api-gateway-to-proxy-amazon-s3-15e24ff174e7
###############################################################################
resource "aws_api_gateway_resource" "index" {
  path_part   = "index"
  parent_id   = aws_api_gateway_rest_api.facialrecognition.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
}

# resource "aws_api_gateway_model" "upload" {
#   rest_api_id  = aws_api_gateway_rest_api.facialrecognition.id
#   name         = "upload"
#   description  = "basic upload JSON schema"
#   content_type = "application/json"

#   schema = file("${path.module}/json/upload_model.json")
# }


resource "aws_api_gateway_method" "index_method" {
  rest_api_id      = aws_api_gateway_rest_api.facialrecognition.id
  resource_id      = aws_api_gateway_resource.index.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = "false"
  # request_models = {
  #   "application/json" = aws_api_gateway_model.upload.name
  # }
  request_parameters = {
    "method.request.path.folder" = true
  }
}

resource "aws_api_gateway_integration" "index" {
  rest_api_id             = aws_api_gateway_rest_api.facialrecognition.id
  resource_id             = aws_api_gateway_resource.index.id
  http_method             = aws_api_gateway_method.index_method.http_method
  integration_http_method = "PUT"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.aws_region}:s3:path/{bucket}/{fileName}"
  credentials             = aws_iam_role.apigateway_s3_uploader.arn
  request_templates = {
    "application/json" = "#set($context.requestOverride.path.fileName = $context.requestId + '.json')\n$input.json('$')"
  }
  request_parameters = {
    "integration.request.path.bucket" = "method.request.path.folder"
  }
}

resource "aws_api_gateway_integration_response" "index" {
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  resource_id = aws_api_gateway_resource.index.id
  http_method = aws_api_gateway_method.index_method.http_method
  status_code = aws_api_gateway_method_response.index_response_200.status_code
  depends_on = [
    aws_api_gateway_integration.index,
    aws_api_gateway_integration.index
  ]
}

resource "aws_api_gateway_method_response" "index_response_200" {
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  resource_id = aws_api_gateway_resource.index.id
  http_method = aws_api_gateway_method.index_method.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {}
}

###############################################################################
# REST API resources - Search
# This is an HTTP Post request, to upload an image file that will be passed
# to a Lambda function that will generate a Rekognition faceprint and then
# search for it in the Rekognition collection.
#
# workflow is: 1. method request        (from Postman, curl, your application, etc.)
#              2. integration request   (we're integrating to an AWS Lambda function)
#              3. integration response  (the results from the Lambda function)
#              4. method response       (hopefully, an http 200 response)
#
###############################################################################
resource "aws_api_gateway_resource" "search" {
  path_part   = "search"
  parent_id   = aws_api_gateway_rest_api.facialrecognition.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
}

resource "aws_api_gateway_method" "search" {
  rest_api_id      = aws_api_gateway_rest_api.facialrecognition.id
  resource_id      = aws_api_gateway_resource.search.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = "true"
}

resource "aws_api_gateway_integration" "search" {
  rest_api_id             = aws_api_gateway_rest_api.facialrecognition.id
  resource_id             = aws_api_gateway_resource.search.id
  http_method             = aws_api_gateway_method.search.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.search.invoke_arn
  content_handling        = "CONVERT_TO_TEXT"
}

resource "aws_api_gateway_method_response" "search_response_200" {
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  resource_id = aws_api_gateway_resource.search.id
  http_method = aws_api_gateway_method.search.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {}
}

resource "aws_lambda_permission" "search" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.search.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.facialrecognition.id}/*/${aws_api_gateway_method.search.http_method}${aws_api_gateway_resource.search.path}"
}
