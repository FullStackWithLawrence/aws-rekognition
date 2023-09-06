#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date:       sep-2023
#
# usage:      override default variable values
#------------------------------------------------------------------------------

###############################################################################
# AWS CLI parameters
###############################################################################
aws_account_id = "090511222473"
aws_region     = "us-east-1"
aws_profile    = "lawrence"
tags = {
  "terraform" = "true",
  "project"   = "Facial Recognition microservice"
  "contact"   = "lpm0073@gmail.com"
}

###############################################################################
# Lambda parameters
###############################################################################
lambda_python_runtime = "python3.11"
debug_mode            = false
lambda_memory_size    = 512
lambda_timeout        = 60

###############################################################################
# CloudWatch logging parameters
###############################################################################
logging_level      = "INFO"
log_retention_days = 3

###############################################################################
# Rekognition index_faces() optional parameters
###############################################################################
max_faces_count            = 10
face_detect_threshold      = 10
face_detect_attributes     = "DEFAULT"
face_detect_quality_filter = "AUTO"

###############################################################################
# APIGateway parameters
###############################################################################
root_domain                = "lawrencemcdaniel.com"
shared_resource_identifier = "facialrecognition"
stage                      = "v1"

# Maximum number of requests that can be made in a given time period.
quota_settings_limit = 500

# Number of requests subtracted from the given limit in the initial time period.
quota_settings_offset = 0

# Time period in which the limit applies. Valid values are "DAY", "WEEK" or "MONTH".
quota_settings_period = "DAY"

# The API request burst limit, the maximum rate limit over a time ranging from one to a few seconds,
# depending upon whether the underlying token bucket is at its full capacity.
throttle_settings_burst_limit = 5

# The API request steady-state rate limit.
throttle_settings_rate_limit = 10

