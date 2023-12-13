# AWS Rekognition REST API

[![FullStackWithLawrence](https://a11ybadges.com/badge?text=FullStackWithLawrence&badgeColor=orange&logo=youtube&logoColor=282828)](https://www.youtube.com/@FullStackWithLawrence)<br>
[![Python](https://a11ybadges.com/badge?logo=python)](https://www.python.org/)
[![Amazon AWS](https://a11ybadges.com/badge?logo=amazonaws)](https://aws.amazon.com/)
[![Terraform](https://a11ybadges.com/badge?logo=terraform)](https://www.terraform.io/)<br>
[![12-Factor](https://img.shields.io/badge/12--Factor-Compliant-green.svg)](./doc/Twelve_Factor_Methodology.md)
[![Unit Tests](https://github.com/FullStackWithLawrence/aws-rekognition/actions/workflows/tests.yml/badge.svg)](https://github.com/FullStackWithLawrence/aws-rekognition/actions)
![GHA pushMain Status](https://img.shields.io/github/actions/workflow/status/FullStackWithLawrence/aws-rekognition/pushMain.yml?branch=main)
![Auto Assign](https://github.com/FullStackwithLawrence/aws-rekognition/actions/workflows/auto-assign.yml/badge.svg)[![Source
code](https://img.shields.io/static/v1?logo=github&label=Git&style=flat-square&color=orange&message=Source%20code)](https://github.com/FullStackWithLawrence/aws-rekognition)
[![Release Notes](https://img.shields.io/github/release/FullStackWithLawrence/aws-rekognition)](https://github.com/FullStackWithLawrence/aws-rekognition/releases)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![hack.d Lawrence McDaniel](https://img.shields.io/badge/hack.d-Lawrence%20McDaniel-orange.svg)](https://lawrencemcdaniel.com)

A facial recognition microservice built with AWS Rekognition, DynamoDB, S3, API Gateway and Lambda.

## Usage

Index and store a face print:

```console
curl --location --globoff --request PUT 'https://api.rekognition.yourdomain.com/v1/index/Image-With-a-Face.jpg' \
--header 'x-api-key: YOUR-API-KEY' \
--header 'Content-Type: text/plain' \
--data '@'
```

Search an image for known faces:

```console
curl --location --globoff --request PUT 'https://api.rekognition.yourdomain.com/v1/search/' \
--header 'x-api-key: YOUR-API-KEY' \
--header 'Content-Type: text/plain' \
--data '@/Users/mcdaniel/Desktop/aws-rekognition/test-data/Different-Image-With-Same-Face.jpg'
```

## Quickstart Setup

This is a fully automated build process using Terraform. The build typically takes around 60 seconds to complete. If you are new to Terraform then please review this [Getting Started Guide](./doc/TERRAFORM.md) first.

Configure Terraform for your AWS account. Set these three values in [terraform.tfvars](./terraform/terraform.tfvars):

```terraform
account_id           = "012345678912"   # your 12-digit AWS account number
aws_region           = "us-east-1"      # an AWS data center
aws_profile          = "default"        # for aws cli credentials
```

Build and configure AWS cloud infrastructure:

```terraform
cd terraform
terraform init
terraform plan
terraform apply
```

## API Key features

- Highly secure. This project follows best practices for handling AWS credentials. The API runs over https using AWS managed SSL/TLS encryption certificates. The API uses an api key. User data is persisted to a non-public AWS S3 bucket.
- Excellent [CloudWatch](https://aws.amazon.com/cloudwatch/) logs for Lambda as well as API Gateway
- Low-cost [AWS serverless](https://aws.amazon.com/serverless/) implementation using [AWS API Gateway](https://aws.amazon.com/api-gateway/) and [AWS Lambda](https://aws.amazon.com/lambda/); free or nearly free in most cases
- Robust, performant and infinitely scalable
- Deploys to a custom domain over https
- Preconfigured [Postman](https://www.postman.com/) files for testing
- includes AWS API Gateway usage policy and api key
- Full CORS configuration

## Requirements

- [AWS account](https://aws.amazon.com/)
- [AWS Command Line Interface](https://aws.amazon.com/cli/)
- [Terraform](https://www.terraform.io/).
  _If you're new to Terraform then see [Getting Started With AWS and Terraform](./doc/TERRAFORM.md)_
- [Python 3.11](https://www.python.org/downloads/): for creating virtual environment used for building AWS Lambda Layer, and locally by pre-commit linters and code formatters.
- [NodeJS](https://nodejs.org/en/download): used with NPM for local ReactJS developer environment, and for configuring/testing Semantic Release.

## Documentation

Please see this [detailed technical summary](./doc/README.md) of the architecture strategy for this solution.

## Support

To get community support, go to the official [Issues Page](https://github.com/FullStackWithLawrence/aws-rekognition/issues) for this project.

## Good Coding Best Practices

This project demonstrates a wide variety of good coding best practices for managing mission-critical cloud-based micro services in a team environment, namely its adherence to [12-Factor Methodology](./doc/Twelve_Factor_Methodology.md). Please see this [Code Management Best Practices](./doc/GOOD_CODING_PRACTICE.md) for additional details.

We want to make this project more accessible to students and learners as an instructional tool while not adding undue code review workloads to anyone with merge authority for the project. To this end we've also added several pre-commit code linting and code style enforcement tools, as well as automated procedures for version maintenance of package dependencies, pull request evaluations, and semantic releases.

## Contributing

We welcome contributions! There are a variety of ways for you to get involved, regardless of your background. In addition to Pull requests, this project would benefit from contributors focused on documentation and how-to video content creation, testing, community engagement, and stewards to help us to ensure that we comply with evolving standards for the ethical use of AI.

For developers, please see:

- the [Developer Setup Guide](./doc/CONTRIBUTING.md)
- and these [commit comment guidelines](./doc/SEMANTIC_VERSIONING.md) 😬😬😬 for managing CI rules for automated semantic releases.

You can also contact [Lawrence McDaniel](https://lawrencemcdaniel.com/contact) directly.
