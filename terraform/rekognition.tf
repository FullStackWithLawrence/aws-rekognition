resource "null_resource" "create-rekognition-collection" {

  triggers = {
    collection = local.aws_rekognition_collection_id
    region     = var.aws_region
    profile    = var.aws_profile
  }

  provisioner "local-exec" {
    when    = create
    command = "aws rekognition create-collection --collection-id ${self.triggers.collection} --region ${self.triggers.region} --profile ${self.triggers.profile}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "aws rekognition delete-collection --collection-id ${self.triggers.collection} --region ${self.triggers.region} --profile ${self.triggers.profile}"
  }
}
