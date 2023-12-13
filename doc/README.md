# Technical Overview of this Architecture

As of Sep-2023 AWS has introduced a large and still-growing [list of AI/ML services](https://aws.amazon.com/getting-started/decision-guides/machine-learning-on-aws-how-to-choose/) that seamlessly interoperate with other infrastructure and services in the AWS ecosystem. This solution is based fundamentally on AWS Rekognition, one of AWS' two vision services.

![AWS ML Stack](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/aws-ml-stack.png "AWS ML Stack")

Additionally, this solution leverages the following AWS serverless services:

- **[Rekognition](https://aws.amazon.com/rekognition/)**: a cloud-based software as a service computer vision platform that was launched in 2016. It is an AWS managed Machine Learning Service with Content moderation, Face compare and search, Face Detection and analysis, Labeling, Custom labels, Text detection, Celebrity recognition, Video segment detection and Streaming Video Events detection features. It is used by a number of United States government agencies, including U.S. Immigration and Customs Enforcement and Orlando, Florida police, as well as private entities.
- **[IAM](https://aws.amazon.com/iam/)**: a web service that helps you securely control access to AWS resources. With IAM, you can centrally manage permissions that control which AWS resources users can access. You use IAM to control who is authenticated (signed in) and authorized (has permissions) to use resources.
- **[S3](https://aws.amazon.com/s3/)**: Amazon Simple Storage Service is a service offered by Amazon Web Services that provides object storage through a web service interface. Amazon S3 uses the same scalable storage infrastructure that Amazon.com uses to run its e-commerce network.
- **[DynamoDB](https://aws.amazon.com/dynamodb/)**: a fully managed proprietary NoSQL database offered by Amazon.com as part of the Amazon Web Services portfolio. DynamoDB offers a fast persistent Key-Value Datastore with built-in support for replication, autoscaling, encryption at rest, and on-demand backup among other features.
- **[Lambda](https://aws.amazon.com/lambda/)**: an event-driven, serverless computing platform provided by Amazon as a part of Amazon Web Services. It is a computing service that runs code in response to events and automatically manages the computing resources required by that code. It was introduced on November 13, 2014.
- **[API Gateway](https://aws.amazon.com/api-gateway/)**: an AWS service for creating, publishing, maintaining, monitoring, and securing REST, HTTP, and WebSocket APIs at any scale.
- **[Certificate Manager](https://aws.amazon.com/certificate-manager/)**: handles the complexity of creating, storing, and renewing public and private SSL/TLS X.509 certificates and keys that protect your AWS websites and applications.
- **[Route53](https://aws.amazon.com/route53/)**: a scalable and highly available Domain Name System service. Released on December 5, 2010.
- **[CloudWatch](https://aws.amazon.com/cloudwatch/)**: CloudWatch enables you to monitor your complete stack (applications, infrastructure, network, and services) and use alarms, logs, and events data to take automated actions and reduce mean time to resolution (MTTR).

## Facial Recognition Index Workflow

Deploys a URL endpoint for uploading an Image file to S3. S3 is configured to invoke a Lambda function on 'put' events. The Lambda function sends the image file to Rekognition, which will analyze the contents for any facial features found, returning a [JSON file of this format](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/rekognition_index_faces.json). Individual facial features are persistened in DynamoDB, and are searchable by Rekognition 'faceprint'.

![Facial Recognition Index Workflow](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/diagram-index.png "Facial Recognition Index Workflow")

## Facial Recognition Search Workflow

Deploys a URL endpoint for uploading an image file to be analyzed by Rekognition. The 'faceprint' of the dominant face in the image is searched against all indexed faces in DynamoDB. Usually, this will be the largest face in the image, but the algorithm also considers other factors, including facial angle to the camera. Returns a [JSON file of this format](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/rekogition_search_faces_by_image.json).

![Facial Recognition Search Workflow](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/diagram-search.png "Facial Recognition Search Workflow")

## Trouble Shooting and Logging

The terraform scripts will automatically create a collection of CloudWatch Log Groups. Additionally, note the Terraform global variable 'debug_mode' (defaults to 'true') which will increase the verbosity of log entries in the [Lambda functions](./terraform/python/), which are implemented with Python.

I refined the contents and formatting of each log group to suit my own needs while building this solution, and in particular while coding the Python Lambda functions.

![CloudWatch Logs](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/cloudwatch-1.png "CloudWatch Logs")
![CloudWatch Logs](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/cloudwatch-2.png "CloudWatch Logs")

## Working With DynamoDB

Index faces are persisted to a DynamoDB table as per the two screen shots below. The AWS DynamoDB console includes a useful query tool named [PartiQL](https://partiql.org/) which you can use to inspect your Rekognition output. See this [sample DynamoDB Rekognition output file](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/dynamodb-sample-records.json).

![DynamoDB console](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/dynamodb-1.png "DynamoDB console")
![DynamoDB query](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/dynamodb-2.png "DynamoDB query")

## Working With S3

Indexed images are persisted to S3, essantially as an archive as well as for future development of additional features such as an endpoint to download indexed images and their corresponding Rekognition faceprint output.

![S3 Console](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/doc/img/s3-1.png "S3 Console")

## Working With Image Data in Postman, AWS Route53 and AWS Rekognition

This solution passes large image files around to and from various large opaque backend services. Take note that using Postman to transport these image files from your local computer to AWS requires that we first [base64-encode](https://en.wikipedia.org/wiki/Base64) the file. Base64 encoding schemes are commonly used to encode binary data, like image files, for storage or transfer over media that can only deal with ASCII text.

This repo includes a utility script [base64encode.sh](../base64encode.sh) that you can use to encode your test images prior to uploading these with Postman.

## Original Sources

Much of the code in this repository was scaffolded from these examples that I found via Google and Youtube searches. Several of these are well-presented, and they provide additional instruction and explanetory theory that I've omitted, so you might want to give these a look.

- [YouTube - Create your own Face Recognition Service with AWS Rekognition, by Tech Raj](https://www.youtube.com/watch?v=oHSesteFK5c)
- [Personnel Recognition with AWS Rekognition — Part I](https://aws.plainenglish.io/personnel-recognition-with-aws-rekognition-part-i-c4530f9b3c74)
- [Personnel Recognition with AWS Rekognition — Part II](https://aws.plainenglish.io/personnel-recognition-with-aws-rekognition-part-ii-c6e9100709b5)
- [Webhook for S3 Bucket By Terraform (REST API in API Gateway to proxy Amazon S3)](https://medium.com/@ekantmate/webhook-for-s3-bucket-by-terraform-rest-api-in-api-gateway-to-proxy-amazon-s3-15e24ff174e7)
- [how to use AWS API Gateway URL end points with Postman](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-usage-plans-with-rest-api.html#api-gateway-usage-plan-test-with-postman)
- [Testing API Gateway Endpoints](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-usage-plans-with-rest-api.html#api-gateway-usage-plan-test-with-postman)
- [How do I upload an image or PDF file to Amazon S3 through API Gateway?](https://repost.aws/knowledge-center/api-gateway-upload-image-s3)
- [Upload files to S3 using API Gateway - Step by Step Tutorial](https://www.youtube.com/watch?v=Q_2CIivxVVs)
- [Tutorial: Create a REST API as an Amazon S3 proxy in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/integrating-api-with-aws-services-s3.html)
