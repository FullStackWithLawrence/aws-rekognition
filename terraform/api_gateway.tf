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

# see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_rest_api
resource "aws_api_gateway_rest_api" "facialrecognition" {
  name        = local.api_name
  description = "Facial recognition micro service"
  binary_media_types = [
    "image/jpeg"
  ]
  api_key_source = "HEADER"
  endpoint_configuration {
    types = ["EDGE"]
  }

  tags = var.tags
}
resource "aws_api_gateway_api_key" "facialrecognition" {
  name = var.shared_resource_identifier
  tags = var.tags
}


resource "aws_api_gateway_deployment" "facialrecognition" {
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  depends_on = [
    aws_api_gateway_integration.index_put,
    aws_api_gateway_integration.search
  ]
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.facialrecognition.body,
      aws_api_gateway_integration.index_put.id,
      aws_api_gateway_integration.search.id
    ]))
  }
  lifecycle {
    create_before_destroy = true
  }
}
# see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_stage
resource "aws_api_gateway_stage" "facialrecognition" {
  deployment_id      = aws_api_gateway_deployment.facialrecognition.id
  cache_cluster_size = "0.5"
  rest_api_id        = aws_api_gateway_rest_api.facialrecognition.id
  stage_name         = var.stage
  tags               = var.tags
}

resource "aws_api_gateway_method_settings" "facialrecognition" {
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  stage_name  = aws_api_gateway_stage.facialrecognition.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled        = true
    data_trace_enabled     = true
    logging_level          = var.logging_level
    throttling_burst_limit = var.throttle_settings_burst_limit
    throttling_rate_limit  = var.throttle_settings_rate_limit
  }
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
  description        = "Allows API Gateway to push files to an S3 bucket"
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
resource "aws_api_gateway_resource" "index_root" {
  parent_id   = aws_api_gateway_rest_api.facialrecognition.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  path_part   = "index"
}

# see https://stackoverflow.com/questions/39040739/in-terraform-how-do-you-specify-an-api-gateway-endpoint-with-a-variable-in-the
resource "aws_api_gateway_resource" "index" {
  parent_id   = aws_api_gateway_resource.index_root.id
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  path_part   = "{filename}"
}

# see https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_method
resource "aws_api_gateway_method" "index_put" {
  rest_api_id      = aws_api_gateway_rest_api.facialrecognition.id
  resource_id      = aws_api_gateway_resource.index.id
  http_method      = "PUT"
  authorization    = "NONE"
  api_key_required = "true"
  request_parameters = {
    "method.request.path.filename" = true
  }
}

resource "aws_api_gateway_integration" "index_put" {
  rest_api_id             = aws_api_gateway_rest_api.facialrecognition.id
  resource_id             = aws_api_gateway_resource.index.id
  http_method             = aws_api_gateway_method.index_put.http_method
  integration_http_method = "PUT"
  type                    = "AWS"

  passthrough_behavior = "WHEN_NO_TEMPLATES"
  content_handling     = "CONVERT_TO_TEXT"

  # For AWS integrations, the URI should be of the form
  #   arn:aws:apigateway:{region}:{subdomain.service|service}:{path|action}/{service_api}
  #   arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:012345678901:function:my-func/invocations
  #   arn:aws:apigateway:ap-southeast-2:s3:path/{bucket}/{fileName}
  #   arn:aws:apigateway:${var.aws_region}:s3:path/${module.s3_bucket.s3_bucket_id}/{key}
  uri         = "arn:aws:apigateway:${var.aws_region}:s3:path/${module.s3_bucket.s3_bucket_id}/{filename}"
  credentials = aws_iam_role.apigateway_s3_uploader.arn

  request_parameters = {
    "integration.request.path.filename" = "method.request.path.filename"
  }

  # see https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
  # request_templates = {
  #   "application/json" = file("${path.module}/json/apigateway_index_request_template.json.tpl")
  # }
  # request_templates       = {
  #   "image/jpeg" = "#set($context.requestOverride.path.filename = $context.requestId + '.json')\n$input.json('$')"
  # }

}

resource "aws_api_gateway_method_response" "index_response_200" {
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  resource_id = aws_api_gateway_resource.index.id
  http_method = aws_api_gateway_method.index_put.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {}
}

resource "aws_api_gateway_integration_response" "index_put" {
  rest_api_id = aws_api_gateway_rest_api.facialrecognition.id
  resource_id = aws_api_gateway_resource.index.id
  http_method = aws_api_gateway_method.index_put.http_method
  status_code = aws_api_gateway_method_response.index_response_200.status_code

  depends_on = [
    aws_api_gateway_integration.index_put
  ]
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
