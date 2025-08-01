#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date: sep-2023
#
# usage:  implement a custom domain for API Gateway endpoint.
#
#         OPTIONAL. UNCOMMENT THIS MODULE IF YOU HAVE A ROOT DOMAIN
#         MANAGED BY AWS ROUTE53.
#------------------------------------------------------------------------------

# see https://registry.terraform.io/providers/-/aws/4.51.0/docs/resources/api_gateway_domain_name
resource "aws_api_gateway_domain_name" "rekognition" {
  count           = var.aws_apigateway_create_custom_domaim ? 1 : 0
  domain_name     = local.api_gateway_subdomain
  certificate_arn = module.acm.acm_certificate_arn
  tags            = var.tags
}

resource "aws_route53_record" "api" {
  count   = var.aws_apigateway_create_custom_domaim ? 1 : 0
  zone_id = data.aws_route53_zone.aws_apigateway_root_domain.id
  name    = local.api_gateway_subdomain
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.rekognition[count.index].cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.rekognition[count.index].cloudfront_zone_id
    evaluate_target_health = false
  }
}

module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 6.0"

  # un-comment this if you choose a region other than us-east-1
  # providers = {
  #   aws = var.aws_region
  # }

  domain_name = local.api_gateway_subdomain
  zone_id     = data.aws_route53_zone.aws_apigateway_root_domain.id

  subject_alternative_names = [
    "*.${local.api_gateway_subdomain}",
  ]
  tags = var.tags

  wait_for_validation = true
}

output "api_custom_apigateway_url" {
  value = "https://${join("", aws_route53_record.api[*].fqdn)}"
}
