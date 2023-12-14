# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test configuration Settings class.

curl --location --request PUT 'https://api.rekognition.lawrencemcdaniel.com/index/Keanu-Reeves.jpg' \
--header 'x-api-key: i3djUnmCAC2HhVdUH5w00akFsAwxa6f6553brnZv' \
--header 'Content-Type: text/plain' \
--data '@/Users/mcdaniel/Desktop/aws-rekognition/terraform/python/rekognition_api/tests/mock_data/img/Keanu-Reeves.jpg'

curl --location --request PUT 'https://api.rekognition.lawrencemcdaniel.com/search/' \
--header 'x-api-key: i3djUnmCAC2HhVdUH5w00akFsAwxa6f6553brnZv' \
--header 'Content-Type: text/plain' \
--data '@/Users/mcdaniel/Desktop/aws-rekognition/terraform/python/rekognition_api/tests/mock_data/img/Keanu-Avril-Mike.jpg'

"""

# python stuff
import json
import os
import socket
import sys
import unittest
from unittest.mock import patch

# 3rd party stuff
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


PYTHON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PYTHON_ROOT)  # noqa: E402


# pylint: disable=too-many-instance-attributes
class TestAWSInfrastructture(unittest.TestCase):
    """Test AWS infrastructure."""

    # Get the working directory of this script
    here = os.path.dirname(os.path.abspath(__file__))

    def env_path(self, filename):
        """Return the path to the .env file."""
        return os.path.join(self.here, filename)

    def setUp(self):
        """Set up test fixtures."""
        env_path = self.env_path(".env")
        load_dotenv(env_path)

        # environment variables
        self.api_key = os.getenv(key="API_KEY")
        self.domain = os.getenv(key="DOMAIN")
        self.s3_bucket_name = os.getenv(key="S3_BUCKET_NAME")
        self.aws_profile = os.getenv(key="AWS_PROFILE")
        self.aws_region = os.getenv(key="AWS_REGION")
        self.common_resource_name = os.getenv(key="DYNAMODB_TABLE_NAME")
        self.api_gateway_name = os.getenv(key="API_GATEWAY_NAME")

        # aws resources
        self.aws_session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
        self.s3_client = self.aws_session.client("s3")
        self.dynamodb = self.aws_session.client("dynamodb")
        self.api_client = self.aws_session.client("apigateway")

    def aws_connection_works(self):
        """Test that the AWS connection works."""
        try:
            # Try a benign operation
            self.s3_client.list_buckets()
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def domain_exists(self):
        """Test that the domain exists."""
        try:
            socket.gethostbyname(self.domain)
            return True
        except socket.gaierror:
            return False

    def bucket_exists(self):
        """Test that the S3 bucket exists."""
        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket_name)
            return True
        except ClientError:
            return False

    def dynamodb_table_exists(self, table_name):
        """Test that the DynamoDB table exists."""
        try:
            response = self.dynamodb.describe_table(TableName=table_name)
            return response["Table"]["TableStatus"] == "ACTIVE"
        except boto3.exceptions.botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return False
            raise

    def api_exists(self, api_name: str):
        """Test that the API Gateway exists."""
        response = self.api_client.get_rest_apis()

        for item in response["items"]:
            if item["name"] == api_name:
                return True
        return False

    def get_api(self, api_name: str) -> json:
        """Test that the API Gateway exists."""
        response = self.api_client.get_rest_apis()

        for item in response["items"]:
            if item["name"] == api_name:
                return item
        return False

    def api_resource_and_method_exists(self, path, method):
        """Test that the API Gateway resource and method exists."""
        api = self.get_api(self.api_gateway_name)
        api_id = api["id"]
        resources = self.api_client.get_resources(restApiId=api_id)
        for resource in resources["items"]:
            if resource["path"] == path:
                try:
                    self.api_client.get_method(restApiId=api_id, resourceId=resource["id"], httpMethod=method)
                    return True
                except self.api_client.exceptions.NotFoundException:
                    return False

        return False

    def get_api_keys(self) -> str:
        """Test that the API Gateway exists."""
        response = self.api_client.get_api_keys(includeValues=True)
        for item in response["items"]:
            if item["name"] == self.common_resource_name:
                return item["value"]
        return False

    def test_aws_connection_works(self):
        """Test that the AWS connection works."""
        self.assertTrue(self.aws_connection_works(), "AWS connection failed.")

    def test_domain_exists(self):
        """Test that settings handles missing .env values."""
        self.assertTrue(self.domain_exists(), f"Domain {self.domain} does not exist.")

    def test_bucket_exists(self):
        """Test that the S3 bucket exists."""
        self.assertTrue(self.bucket_exists(), f"S3 bucket {self.s3_bucket_name} does not exist.")

    def test_dynamodb_table_exists(self):
        """Test that the DynamoDB table exists."""
        self.assertTrue(
            self.dynamodb_table_exists(self.common_resource_name),
            f"DynamoDB table {self.common_resource_name} does not exist.",
        )

    def test_api_exists(self):
        """Test that the API Gateway exists."""
        api = self.get_api(self.api_gateway_name)
        self.assertIsInstance(api, dict, "API Gateway does not exist.")

    def test_api_resource_index_exists(self):
        """Test that the API Gateway index resource exists."""
        self.assertTrue(
            self.api_resource_and_method_exists("/index/{filename}", "PUT"),
            "API Gateway index (PUT) resource does not exist.",
        )

    def test_api_resource_search_exists(self):
        """Test that the API Gateway index resource exists."""
        self.assertTrue(
            self.api_resource_and_method_exists("/search", "ANY"),
            "API Gateway search (ANY) resource does not exist.",
        )

    def test_api_key_exists(self):
        """Test that an API key exists."""
        api_key = self.get_api_keys()
        self.assertIsInstance(api_key, str, "API key does not exist.")
        self.assertGreaterEqual(len(api_key), 15, "API key is too short.")
