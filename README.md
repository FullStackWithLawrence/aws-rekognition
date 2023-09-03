# AWS Rekognition Demo

Facial recognition implementation demo

```shell
aws s3 cp file-to-be-upload.jpg s3://your-awesome-bucket/photos/portrait/ - metadata x-amz-meta-name=Mehmet,x-amz-meta-surname=Gungoren
```

## Alternative Command-line implementation

- [YouTube - Create your own Face Recognition Service with AWS Rekognition, by Tech Raj](https://www.youtube.com/watch?v=oHSesteFK5c)
- [Personnel Recognition with AWS Rekognition — Part I](https://aws.plainenglish.io/personnel-recognition-with-aws-rekognition-part-i-c4530f9b3c74)
- [Personnel Recognition with AWS Rekognition — Part I](https://aws.plainenglish.io/personnel-recognition-with-aws-rekognition-part-ii-c6e9100709b5)

## Introduction

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
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
$ echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/ubuntu/.profile
$ eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

Use homebrew to install all required packages.

```console
$ brew install awscli terraform
```

### Configure the AWS CLI

To configure the AWS CLI run the following command:

```console
$ aws configure
```

This will interactively prompt for your AWS IAM user access key, secret key and preferred region.


### Setup Terraform

Terraform is a declarative open-source infrastructure-as-code software tool created by HashiCorp. This repo leverages Terraform to create all cloud infrastructure as well as to install and configure all software packages that run inside of Kubernetes. Terraform relies on an S3 bucket for storing its state data, and a DynamoDB table for managing a semaphore lock during operations.

Use these three environment variables for creating the uniquely named resources that the Terraform modules in this repo will be expecting to find at run-time.

**IMPORTANT: these three settings should be consistent with the values your set in terraform.tfvars in the next section.**

```console
$ AWS_ACCOUNT=012345678912      # add your 12-digit AWS account number here
$
$ AWS_REGION=us-east-1          # any valid AWS region code.
$ AWS_ENVIRONMENT=rekognition   # any valid string. Keep it short -- 3 characters is ideal.
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
$ AWS_DYNAMODB_TABLE="${AWS_ACCOUNT}-tfstate-lock-${AWS_ENVIRONMENT}"
$ aws dynamodb create-table --region $AWS_REGION --table-name $AWS_DYNAMODB_TABLE  \
               --attribute-definitions AttributeName=LockID,AttributeType=S  \
               --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput  \
               ReadCapacityUnits=1,WriteCapacityUnits=1
```

## II. Build and Deploy WAS

### Step 1. Checkout the repository

```console
$ git clone https://github.com/lpm0073/aws-rekognition.git
```

### Step 2. Change directory to AWS

```console
$ cd ~/WAS-Kubernetes/EnvironmentSetup/AWS/
```

### Step 3. Configure your Terraform backend

Edit the following snippet so that bucket, region and dynamodb_table are consistent with your values of $AWS_REGION, $AWS_S3_BUCKET, $AWS_DYNAMODB_TABLE

```console
$ vim terraform/terraform.tf
```

```terraform
  backend "s3" {
    bucket         = "012345678912-tfstate-rekognition"
    key            = "was/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "012345678912-tfstate-lock-rekognition"
    profile        = "default"
    encrypt        = false
  }
````

### Step 4. Configure your environment by setting Terraform global variable values

```console
$ vim terraform/was/terraform.tfvars
```

Required inputs are as follows:

```terraform
account_id           = "012345678912"
aws_region           = "us-east-1"
domain               = "example.com"
shared_resource_name = "facialrecognition"
```


### Step 5. Run the following command to set up EKS and deploy WAS

The Terraform modules in this repo rely extensively on calls to other third party Terraform modules published and maintained by [AWS](https://registry.terraform.io/namespaces/terraform-aws-modules). These modules will be downloaded by Terraform so that these can be executed locally from your computer. Noteworth examples of such third party modules include:

* [terraform-aws-modules/s3](https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest)
* [terraform-aws-modules/dynamodb](https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/latest)

```console
$ cd terraform
$ terraform init
```

Screen output should resemble the following:
![Terraform init](https://raw.githubusercontent.com/lpm0073/aws-rekognition/main/doc/terraform-init.png "Terraform init")

To deploy the service run the following

```console
$ terraform apply
```
## III. WAS Usage

## IV. Uninstall

The following completely destroys everything including the kubernetes cluster, Wolfram Application Server and all resources:

```console
$ cd terraform
$ terraform init
$ terraform destroy
```

Delete Terraform state management resources

```console
$ AWS_ACCOUNT=012345678912      # add your 12-digit AWS account number here
$ AWS_REGION=us-east-1
$ AWS_ENVIRONMENT=rekognition   # any valid string. Keep it short
$ AWS_S3_BUCKET="${AWS_ACCOUNT}-tfstate-${AWS_ENVIRONMENT}"
$ AWS_DYNAMODB_TABLE="${AWS_ACCOUNT}-tfstate-lock-${AWS_ENVIRONMENT}"
```

To delete the DynamoDB table

```console
$ aws dynamodb delete-table --region $AWS_REGION --table-name $AWS_DYNAMODB_TABLE
```

To delete the AWS S3 bucket

```console
$ aws s3 rm s3://$AWS_S3_BUCKET --recursive
$ aws s3 rb s3://$AWS_S3_BUCKET --force
```
