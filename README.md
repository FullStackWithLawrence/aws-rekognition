[![Source code](https://img.shields.io/static/v1?logo=github&label=Git&style=flat-square&color=brightgreen&message=Source%20code)](https://github.com/FullStackWithLawrence/aws-rekognition)
[![Documentation](https://img.shields.io/static/v1?&label=Documentation&style=flat-square&color=000000&message=Documentation)](https://github.com/FullStackWithLawrence/aws-rekognition)
[![AGPL License](https://img.shields.io/github/license/overhangio/tutor.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![hack.d Lawrence McDaniel](https://img.shields.io/badge/hack.d-Lawrence%20McDaniel-orange.svg)](https://lawrencemcdaniel.com)

# AWS Rekognition Demo

A facial recognition microservice implemented as a REST API.

## Usage

1. base64 encode your image files

```shell
./base64encode ImageWithFaces1.jpg ImageWithFaces1-encoded.jpg
./base64encode ImageWithMoreFaces2.jpg ImageWithMoreFaces2-encoded.jpg
```

2. Use Postman to upload one or more base64-encoded images to the 'index' URL endpoint. This will perform facial recognition analysis, and then index all faces found in the image, storing the indexes in a DynamoDB table.

3. Use Postman to upload a base64-encoded image to the 'search' URL endpoint. This will perform facial analysis on the image and then search the DynamoDB table for any matches. Results are returned in JSON format.

## Architecture

Implements as a REST API that leverages the following additional AWS serverless services:

- **AWS Rekognition**: a cloud-based software as a service computer vision platform that was launched in 2016. It is an AWS managed Machine Learning Service with Content moderation, Face compare and search, Face Detection and analysis, Labeling, Custom labels, Text detection, Celebrity recognition, Video segment detection and Streaming Video Events detection features. It is used by a number of United States government agencies, including U.S. Immigration and Customs Enforcement and Orlando, Florida police, as well as private entities.
- **S3**: Amazon Simple Storage Service is a service offered by Amazon Web Services that provides object storage through a web service interface. Amazon S3 uses the same scalable storage infrastructure that Amazon.com uses to run its e-commerce network.
- **DynamoDB**: a fully managed proprietary NoSQL database offered by Amazon.com as part of the Amazon Web Services portfolio. DynamoDB offers a fast persistent Key-Value Datastore with built-in support for replication, autoscaling, encryption at rest, and on-demand backup among other features.
- **Lambda**: an event-driven, serverless computing platform provided by Amazon as a part of Amazon Web Services. It is a computing service that runs code in response to events and automatically manages the computing resources required by that code. It was introduced on November 13, 2014.
- **API Gateway**: an AWS service for creating, publishing, maintaining, monitoring, and securing REST, HTTP, and WebSocket APIs at any scale.
- **Certificate Manager**: handles the complexity of creating, storing, and renewing public and private SSL/TLS X.509 certificates and keys that protect your AWS websites and applications.
- **Route53**: a scalable and highly available Domain Name System service. Released on December 5, 2010.

### Facial Recognition Index Workflow

![Facial Recognition Index Workflow](https://raw.githubusercontent.com/lpm0073/aws-rekognition/main/doc/diagram-index.png "Facial Recognition Index Workflow")

### Facial Recognition Search Workflow

![Facial Recognition Search Workflow](https://raw.githubusercontent.com/lpm0073/aws-rekognition/main/doc/diagram-search.png "Facial Recognition Search Workflow")

## Working With Image Data in Postman, AWS Route53 and AWS Rekognition

This solution passes large image files around to and from various large opaque backend services. Take note that using Postman to transport these image files from your local computer to AWS requires that we first 'base64' encode the file. Base64 encoding schemes are commonly used to encode binary data, like image files for example, for storage or transfer over media that can only deal with ASCII text.

This repo includes a utility script [base64encode.sh](./base64encode.sh) that you can use to encode your test images prior to uploading these with Postman.

## If You're New To AWS or Terraform

This document describes how to deploy a [AWS Rekognition Service](https://aws.amazon.com/rekognition/) using a combination of AWS resources.

This is a [Terraform](https://www.terraform.io/) based installation methodology that reliably automates the complete build, management and destruction processes of all resources. [Terraform](https://www.terraform.io/) is an [infrastructure-as-code](https://en.wikipedia.org/wiki/Infrastructure_as_code) command line tool that will create and configure all of the approximately two dozen software and cloud infrastructure resources that are needed for running the service on AWS infrastructure. These Terraform scripts will install and configure all cloud infrastructure resources and system software on which the service depends. This process will take around 2 minutes to complete and will generate copious amounts of console output.

The service stack consists of the following:

* a AWS S3 bucket and DynamoDB table for managing Terraform state
* [AWS S3 bucket](https://aws.amazon.com/s3/) for storing train and test image sets.
* [DynamoDB Table](https://aws.amazon.com/dynamodb/) for persisting Rekognition service results
* [AWS IAM Role](https://aws.amazon.com/iam/) for managing service-level role-based security for this service

**WARNINGS**:

**1. The EKS service will create many AWS resources in other parts of your AWS account including EC2, VPC, IAM and KMS. You should not directly modify any of these resources, as this could lead to unintended consequences in the safe operation of your Kubernetes cluster up to and including permanent loss of access to the cluster itself.**

**2. Terraform is a memory intensive application. For best results you should run this on a computer with at least 4Gib of free memory.**

## I. Installation Prerequisites

Quickstart for Linux & macOS operating systems.

**Prerequisite:** Obtain an [AWS IAM User](https://aws.amazon.com/iam/) with administrator priviledges, access key and secret key.

Ensure that your environment includes the latest stable releases of the following software packages:

* [aws cli](https://aws.amazon.com/cli/)
* [terraform](https://www.terraform.io/)

### Install required software packages using Homebrew

If necessary, install [Homebrew](https://brew.sh/)

```console
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/ubuntu/.profile
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

Use homebrew to install all required packages.

```console
brew install awscli terraform
```

### Configure the AWS CLI

To configure the AWS CLI run the following command:

```console
aws configure
```

This will interactively prompt for your AWS IAM user access key, secret key and preferred region.


### Setup Terraform

Terraform is a declarative open-source infrastructure-as-code software tool created by HashiCorp. This repo leverages Terraform to create all cloud infrastructure as well as to install and configure all software packages that run inside of Kubernetes. Terraform relies on an S3 bucket for storing its state data, and a DynamoDB table for managing a semaphore lock during operations.

Use these three environment variables for creating the uniquely named resources that the Terraform modules in this repo will be expecting to find at run-time.

**IMPORTANT: these three settings should be consistent with the values your set in terraform.tfvars in the next section.**

```console
AWS_ACCOUNT=012345678912      # add your 12-digit AWS account number here
$
AWS_REGION=us-east-1          # any valid AWS region code.
AWS_ENVIRONMENT=rekognition   # any valid string. Keep it short -- 3 characters is ideal.
```

First create an AWS S3 Bucket

```console
AWS_S3_BUCKET="${AWS_ACCOUNT}-tfstate-${AWS_ENVIRONMENT}"

# for buckets created in us-east-1
aws s3api create-bucket --bucket $AWS_S3_BUCKET --region $AWS_REGION

# for all other regions
aws s3api create-bucket --bucket $AWS_S3_BUCKET --region $AWS_REGION --create-bucket-configuration LocationConstraint=$AWS_REGION
```

Then create a DynamoDB table

```console
AWS_DYNAMODB_TABLE="${AWS_ACCOUNT}-tfstate-lock-${AWS_ENVIRONMENT}"
aws dynamodb create-table --region $AWS_REGION --table-name $AWS_DYNAMODB_TABLE  \
               --attribute-definitions AttributeName=LockID,AttributeType=S  \
               --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput  \
               ReadCapacityUnits=1,WriteCapacityUnits=1
```

## II. Build and Deploy

### Step 1. Checkout the repository

```console
git clone https://github.com/lpm0073/aws-rekognition.git
```

### Step 2. Configure your Terraform backend

Edit the following snippet so that bucket, region and dynamodb_table are consistent with your values of $AWS_REGION, $AWS_S3_BUCKET, $AWS_DYNAMODB_TABLE

```console
vim terraform/terraform.tf
```

```terraform
  backend "s3" {
    bucket         = "012345678912-tfstate-rekognition"
    key            = "rekognition/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "012345678912-tfstate-lock-rekognition"
    profile        = "default"
    encrypt        = false
  }
````

### Step 4. Configure your environment by setting Terraform global variable values

```console
vim terraform/terraform.tfvars
```

Required inputs are as follows:

```terraform
account_id           = "012345678912"
aws_region           = "us-east-1"
domain               = "example.com"
shared_resource_name = "facialrecognition"
```


### Step 3. Run the following command to initialize and build the solution

The Terraform modules in this repo rely extensively on calls to other third party Terraform modules published and maintained by [AWS](https://registry.terraform.io/namespaces/terraform-aws-modules). These modules will be downloaded by Terraform so that these can be executed locally from your computer. Noteworth examples of such third party modules include:

* [terraform-aws-modules/s3](https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest)
* [terraform-aws-modules/dynamodb](https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/latest)

```console
cd terraform
terraform init
```

Screen output should resemble the following:
![Terraform init](https://raw.githubusercontent.com/lpm0073/aws-rekognition/main/doc/terraform-init.png "Terraform init")

```console
terraform plan
```

Screen output should resemble the following:
![Terraform plan](https://raw.githubusercontent.com/lpm0073/aws-rekognition/main/doc/terraform-plan.png "Terraform plan")

To deploy the service run the following

```console
terraform apply
```

![Terraform apply](https://raw.githubusercontent.com/lpm0073/aws-rekognition/main/doc/terraform-apply2.png "Terraform apply")

## III. Usage

## IV. Uninstall

The following completely destroys all AWS resources. Note that this operation might take up to 20 minutes to complete.

```console
cd terraform
terraform init
terraform destroy
```

Delete Terraform state management resources

```console
AWS_ACCOUNT=012345678912      # add your 12-digit AWS account number here
AWS_REGION=us-east-1
AWS_ENVIRONMENT=rekognition   # any valid string. Keep it short
AWS_S3_BUCKET="${AWS_ACCOUNT}-tfstate-${AWS_ENVIRONMENT}"
AWS_DYNAMODB_TABLE="${AWS_ACCOUNT}-tfstate-lock-${AWS_ENVIRONMENT}"
```

To delete the DynamoDB table

```console
aws dynamodb delete-table --region $AWS_REGION --table-name $AWS_DYNAMODB_TABLE
```

To delete the AWS S3 bucket

```console
aws s3 rm s3://$AWS_S3_BUCKET --recursive
aws s3 rb s3://$AWS_S3_BUCKET --force
```

## Original Sources

Much of the code in this repository was scaffolded from these examples that I found via Google and Youtube searches. Several of these are well-presented, and they provide additional instruction and explanetory theory that I've ommited, so you might want to give these a look.

- [YouTube - Create your own Face Recognition Service with AWS Rekognition, by Tech Raj](https://www.youtube.com/watch?v=oHSesteFK5c)
- [Personnel Recognition with AWS Rekognition — Part I](https://aws.plainenglish.io/personnel-recognition-with-aws-rekognition-part-i-c4530f9b3c74)
- [Personnel Recognition with AWS Rekognition — Part II](https://aws.plainenglish.io/personnel-recognition-with-aws-rekognition-part-ii-c6e9100709b5)
- [Webhook for S3 Bucket By Terraform (REST API in API Gateway to proxy Amazon S3)](https://medium.com/@ekantmate/webhook-for-s3-bucket-by-terraform-rest-api-in-api-gateway-to-proxy-amazon-s3-15e24ff174e7)
- [how to use AWS API Gateway URL end points with Postman](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-usage-plans-with-rest-api.html#api-gateway-usage-plan-test-with-postman)
- [Testing API Gateway Endpoints](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-usage-plans-with-rest-api.html#api-gateway-usage-plan-test-with-postman)
- [How do I upload an image or PDF file to Amazon S3 through API Gateway?](https://repost.aws/knowledge-center/api-gateway-upload-image-s3)
- [Upload files to S3 using API Gateway - Step by Step Tutorial](https://www.youtube.com/watch?v=Q_2CIivxVVs)
- [Tutorial: Create a REST API as an Amazon S3 proxy in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/integrating-api-with-aws-services-s3.html)
