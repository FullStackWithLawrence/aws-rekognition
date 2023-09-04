#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: Feb-2022
#
# usage:  - implement a REST API with a single end point for posting an image.
#         - add a DNS record for the REST API
#         - add TLS/SSL termination for https
#
# see:    https://developer.hashicorp.com/terraform/tutorials/aws/lambda-api-gateway
#------------------------------------------------------------------------------
locals {
  api_gateway_subdomain = "api.${var.shared_resource_identifier}.${var.root_domain}"
}
data "aws_route53_zone" "root_domain" {
  name = var.root_domain
}

data "aws_caller_identity" "current" {}

###############################################################################
# REST API resources
###############################################################################
resource "aws_api_gateway_rest_api" "api" {
  name = "${var.shared_resource_identifier}-api"
}

###############################################################################
# REST API resources - IAM
###############################################################################
resource "aws_iam_role" "s3" {
  name = "${var.shared_resource_identifier}-s3"
  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "",
          "Effect" : "Allow",
          "Principal" : {
            "Service" : "apigateway.amazonaws.com"
          },
          "Action" : "sts:AssumeRole"
        }
      ]
    }
  )
  tags = var.tags
}
resource "aws_iam_role_policy_attachment" "cloudwatch_apigateway" {
  role       = aws_iam_role.s3.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}
resource "aws_iam_role_policy" "ping_data_allow_access" {
  name = "${var.shared_resource_identifier}-apigateway"
  role = aws_iam_role.s3.id
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "VisualEditor0",
          "Effect" : "Allow",
          "Action" : [
            "s3:ListStorageLensConfigurations",
            "s3:ListAccessPointsForObjectLambda",
            "s3:GetAccessPoint",
            "s3:PutAccountPublicAccessBlock",
            "s3:GetAccountPublicAccessBlock",
            "s3:ListAllMyBuckets",
            "s3:ListAccessPoints",
            "s3:PutAccessPointPublicAccessBlock",
            "s3:ListJobs",
            "s3:PutStorageLensConfiguration",
            "s3:ListMultiRegionAccessPoints",
            "s3:CreateJob"
          ],
          "Resource" : "*"
        },
        {
          "Sid" : "VisualEditor1",
          "Effect" : "Allow",
          "Action" : "s3:*",
          "Resource" : [
            "arn:aws:s3:::webhook-apigateway*",
            "arn:aws:s3:::webhook-apigateway/*"
          ]
        }
      ]
    }
  )
}

resource "aws_api_gateway_api_key" "facialrecognition" {
  name = var.shared_resource_identifier

}

###############################################################################
# REST API resources - Index
###############################################################################
# see https://medium.com/@ekantmate/webhook-for-s3-bucket-by-terraform-rest-api-in-api-gateway-to-proxy-amazon-s3-15e24ff174e7
resource "aws_api_gateway_model" "upload" {
  rest_api_id  = aws_api_gateway_rest_api.api.id
  name         = "upload"
  description  = "basic upload JSON schema"
  content_type = "application/json"

  schema = file("${path.module}/json/upload_model.json")
}


resource "aws_api_gateway_resource" "index" {
  path_part   = "index"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "index_method" {
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.index.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = "true"
  request_models = {
    "application/json" = aws_api_gateway_model.upload.name
  }
  request_parameters = {
    "method.request.path.folder" = true
  }

}

resource "aws_api_gateway_integration" "index" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.index.id
  http_method             = aws_api_gateway_method.index_method.http_method
  integration_http_method = "PUT"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${var.aws_region}:s3:path/{bucket}/{fileName}"
  credentials             = aws_iam_role.s3.arn
  request_templates = {
    "application/json" = "#set($context.requestOverride.path.fileName = $context.requestId + '.json')\n$input.json('$')"
  }
  request_parameters = {
    "integration.request.path.bucket" = "method.request.path.folder"
  }
}

resource "aws_api_gateway_method_response" "index_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.index.id
  http_method = aws_api_gateway_method.index_method.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {}
}
resource "aws_api_gateway_integration_response" "post" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.index.id
  http_method = aws_api_gateway_method.index_method.http_method
  status_code = aws_api_gateway_method_response.index_response_200.status_code
  depends_on = [
    aws_api_gateway_integration.index,
    aws_api_gateway_integration.index
  ]
}


###############################################################################
# REST API resources - Search
###############################################################################
resource "aws_api_gateway_resource" "search" {
  path_part   = "search"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "search_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.search.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "search" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.search.id
  http_method             = aws_api_gateway_method.search_method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.search_function.invoke_arn
  content_handling        = "CONVERT_TO_TEXT"
}

resource "aws_api_gateway_method_response" "search_response_200" {
  rest_api_id         = aws_api_gateway_rest_api.api.id
  resource_id         = aws_api_gateway_resource.search.id
  http_method         = aws_api_gateway_method.search_method.http_method
  status_code         = "200"
  response_models     = {}
  response_parameters = {}
}

resource "aws_lambda_permission" "search_function" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.search_function.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.search_method.http_method}${aws_api_gateway_resource.search.path}"
}

resource "aws_api_gateway_deployment" "facialrecognition" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = var.stage

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_resource.search,
    aws_api_gateway_method.search_method,
    aws_api_gateway_integration.search
  ]
}

###############################################################################
# URL end point
###############################################################################
module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "4.3"

  # un-comment this is you choose a region other than us-east-1
  # providers = {
  #   aws = var.aws_region
  # }

  domain_name = local.api_gateway_subdomain
  zone_id     = data.aws_route53_zone.root_domain.id

  subject_alternative_names = [
    "*.${local.api_gateway_subdomain}",
  ]
  tags = var.tags

  wait_for_validation = true
}
resource "aws_api_gateway_domain_name" "domain_name" {
  domain_name     = local.api_gateway_subdomain
  certificate_arn = module.acm.acm_certificate_arn
}

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.root_domain.id
  name    = local.api_gateway_subdomain
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.domain_name.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.domain_name.cloudfront_zone_id
    evaluate_target_health = false
  }
}
