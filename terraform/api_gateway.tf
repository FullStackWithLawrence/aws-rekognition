locals {
  api_gateway_subdomain = "api.${var.shared_resource_identifier}.${var.root_domain}"
}
data "aws_route53_zone" "root_domain" {
  name = var.root_domain
}

data "aws_caller_identity" "current" {}
output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

resource "aws_api_gateway_rest_api" "api" {
  name = "recognition-api"
}

resource "aws_api_gateway_resource" "search" {
  path_part   = "search"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.search.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.search.id
  http_method             = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = aws_lambda_function.search_function.invoke_arn
  content_handling        = "CONVERT_TO_TEXT"
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id         = aws_api_gateway_rest_api.api.id
  resource_id         = aws_api_gateway_resource.search.id
  http_method         = aws_api_gateway_method.method.http_method
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
  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.method.http_method}${aws_api_gateway_resource.search.path}"
}

resource "aws_api_gateway_deployment" "apig_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "apig"

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_resource.search,
    aws_api_gateway_method.method,
    aws_api_gateway_integration.integration
  ]
}

module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "4.3"

  # providers = {
  #   aws = var.aws_region
  # }

  domain_name = var.root_domain
  zone_id     = data.aws_route53_zone.root_domain.id

  subject_alternative_names = []
  tags = var.tags

  wait_for_validation = true
}
resource "aws_api_gateway_domain_name" "domain_name" {
  domain_name = local.api_gateway_subdomain
  certificate_arn = "${module.acm.acm_certificate_arn}"
}

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.root_domain.id
  name    = local.api_gateway_subdomain
  type    = "A"

  alias {
    name                   = "${aws_api_gateway_domain_name.domain_name.cloudfront_domain_name}"
    zone_id                = "${aws_api_gateway_domain_name.domain_name.cloudfront_zone_id}"
    evaluate_target_health = false
  }
}
