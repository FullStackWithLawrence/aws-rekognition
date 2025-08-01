
module "dynamodb_table" {
  # see https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/latest
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "~> 5.0"

  name                        = local.table_name
  hash_key                    = "FaceId"
  table_class                 = "STANDARD"
  deletion_protection_enabled = false
  billing_mode                = "PROVISIONED"
  read_capacity               = 5
  write_capacity              = 5


  attributes = [
    {
      name = "FaceId"
      type = "S"
    }
  ]

  tags = var.tags
}
