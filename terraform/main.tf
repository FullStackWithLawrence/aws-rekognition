
#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date:       sep-2023
#
# usage:      build AWS infrastructure for a Rekognition solution
#------------------------------------------------------------------------------
locals {
    collection_id = "${var.shared_resource_identifier}-collection"
    table_name = var.shared_resource_identifier
}

resource "random_id" "hash" {
  byte_length = 16
}

module "personnel_bucket" {
    # see https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest
    source = "terraform-aws-modules/s3-bucket/aws"
    version = "~> 3.14"

    bucket = "${var.aws_account_id}-${var.shared_resource_identifier}-${random_id.hash.hex}"
    acl    = "private"

    versioning = {
    enabled = false
    }
    tags = var.tags
}


module "dynamodb_table" {
    # see https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/latest
    source   = "terraform-aws-modules/dynamodb-table/aws"
    version = "~> 3.3"

    name                        = local.table_name
    hash_key                    = "RekognitionId"
    table_class                 = "STANDARD"
    deletion_protection_enabled = false
    billing_mode   = "PROVISIONED"
    read_capacity  = 5
    write_capacity = 5


    attributes = [
    {
        name = "RekognitionId"
        type = "S"
    }
    ]

    tags = var.tags
}


resource "null_resource" "create-rekognition-collection" {

  triggers = {
    collection = local.collection_id
    region = var.aws_region
  }

  provisioner "local-exec" {
    when    = create
    command = "aws rekognition create-collection --collection-id ${self.triggers.collection} --region ${self.triggers.region}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "aws rekognition delete-collection --collection-id ${self.triggers.collection} --region ${self.triggers.region}"
  }
}
