#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date:       sep-2023
#
# usage:      all Terraform variable declarations
#------------------------------------------------------------------------------
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

variable "root_domain" {
  description = "a valid Internet domain name which you directly control using AWS Route53 in this account"
  type        = string
}

variable "shared_resource_identifier" {
  description = "A common identifier/prefix for resources created for this demo"
  type        = string
  default     = "facialrecognition"
}

variable "stage" {
  description = "Examples: dev, staging, prod"
  type        = string
  default     = "prod"
}
variable "tags" {
  description = "A map of tags to add to all resources. Tags added to launch configuration or templates override these values."
  type        = map(string)
  default     = {}
}

variable "max_faces_count" {
  type    = number
  default = 10
}
variable "face_detect_threshold" {
  type    = number
  default = 10
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
