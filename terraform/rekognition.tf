resource "null_resource" "create-rekognition-collection" {

  triggers = {
    collection = local.collection_id
    region     = var.aws_region
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
