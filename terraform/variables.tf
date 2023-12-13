#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date:       sep-2023
#
# usage:      all Terraform variable declarations
#------------------------------------------------------------------------------
variable "debug_mode" {
  type    = bool
  default = false
}
variable "aws_profile" {
  description = "a valid AWS CLI profile located in $HOME/.aws/credentials"
  type        = string
  default     = "default"
}
variable "aws_region" {
  description = "A valid AWS data center region code"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "12-digit AWS account number"
  type        = string
}
variable "tags" {
  description = "A map of tags to add to all resources. Tags added to launch configuration or templates override these values."
  type        = map(string)
  default     = {}
}


variable "root_domain" {
  description = "a valid Internet domain name which you directly control using AWS Route53 in this account"
  type        = string
}

variable "shared_resource_identifier" {
  description = "A common identifier/prefix for resources created for this demo"
  type        = string
  default     = "rekognition"
}

variable "stage" {
  description = "Examples: dev, staging, prod, v0, v1, etc."
  type        = string
  default     = "v1"
}

variable "logging_level" {
  type    = string
  default = "INFO"
}
variable "log_retention_days" {
  type    = number
  default = 3
}
variable "max_faces_count" {
  type    = number
  default = 10
}
variable "face_detect_threshold" {
  type    = number
  default = 10
}

# The QualityFilter input parameter allows you to filter out detected faces that don’t
# meet a required quality bar. The quality bar is based on a variety of common use cases.
# Use QualityFilter to set the quality bar for filtering by specifying LOW, MEDIUM, or HIGH.
# If you do not want to filter detected faces, specify NONE. The default value is NONE.
variable "face_detect_quality_filter" {
  description = "'NONE'|'AUTO'|'LOW'|'MEDIUM'|'HIGH'"
  type        = string
  default     = "AUTO"
}
variable "face_detect_attributes" {
  description = "'DEFAULT'|'ALL'"
  type        = string
  default     = "DEFAULT"
}
variable "quota_settings_limit" {
  type    = number
  default = 20
}

variable "quota_settings_offset" {
  type    = number
  default = 2
}

variable "quota_settings_period" {
  type    = string
  default = "WEEK"
}

variable "throttle_settings_burst_limit" {
  type    = number
  default = 5
}
variable "throttle_settings_rate_limit" {
  type    = number
  default = 10
}

variable "lambda_python_runtime" {
  type    = string
  default = "python3.11"
}
variable "lambda_memory_size" {
  description = "Lambda function memory allocations in Mb"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}
