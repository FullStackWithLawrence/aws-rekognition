output "stage" {
  value = var.stage
}
output "api_gateway_arn" {
  value = aws_api_gateway_deployment.apig_deployment.id
}

output "api_gateway_subdomain" {
  value = aws_route53_record.api.fqdn
}

output "lambda_index" {
  value = aws_lambda_function.index_function.arn
}

output "lambda_search" {
  value = aws_lambda_function.search_function.arn
}

output "s3_bucket" {
  value = module.personnel_bucket.s3_bucket_bucket_domain_name
}

output "dynamodb_table" {
  value = module.dynamodb_table.dynamodb_table_arn
}
