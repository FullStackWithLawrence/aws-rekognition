#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: sep-2023
#
# usage:  implement a custom domain for API Gateway endpoint.
#
#         OPTIONAL. DELETE THIS MODULE IF YOU DO NOT HAVE A
#         ROOT DOMAIN MANAGED BY AWS ROUTE53.
#------------------------------------------------------------------------------

resource "aws_api_gateway_domain_name" "facialrecognition" {
  domain_name     = local.api_gateway_subdomain
  certificate_arn = module.acm.acm_certificate_arn
  tags            = var.tags
}

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.root_domain.id
  name    = local.api_gateway_subdomain
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.facialrecognition.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.facialrecognition.cloudfront_zone_id
    evaluate_target_health = false
  }
}

module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 4.3"

  # un-comment this if you choose a region other than us-east-1
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
