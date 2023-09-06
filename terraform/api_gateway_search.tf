###############################################################################
# REST API resources - Search
# This is an HTTP Put request, to upload an image file that will be passed
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
  http_method      = "ANY"
  authorization    = "NONE"
  api_key_required = "true"
}

resource "aws_api_gateway_integration" "search" {
  rest_api_id             = aws_api_gateway_rest_api.facialrecognition.id
  resource_id             = aws_api_gateway_resource.search.id
  http_method             = aws_api_gateway_method.search.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.search.invoke_arn
}
resource "aws_lambda_permission" "search" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.search.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.facialrecognition.id}/*/${aws_api_gateway_method.search.http_method}${aws_api_gateway_resource.search.path}"

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
