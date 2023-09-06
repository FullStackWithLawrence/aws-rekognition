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
  uri                     = "arn:aws:apigateway:${var.aws_region}:s3:path/${module.s3_bucket.s3_bucket_id}/{filename}"
  credentials             = aws_iam_role.apigateway.arn

  # https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-payload-encodings-workflow.html
  # returns "Execution failed due to configuration error: Unable to base64 decode the body."
  content_handling = "CONVERT_TO_BINARY"
  #content_handling = "CONVERT_TO_TEXT"
  request_parameters = {
    "integration.request.path.filename" = "method.request.path.filename"
  }
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
