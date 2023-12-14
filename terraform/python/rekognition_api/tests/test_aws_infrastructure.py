# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test configuration Settings class."""

# python stuff
import json
import os
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# 3rd party stuff
import boto3
import hcl2
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(HERE))
TERRAFORM_ROOT = str(Path(PYTHON_ROOT).parent)
TERRAFORM_TFVARS = os.path.join(TERRAFORM_ROOT, "terraform.tfvars")

# our stuff
sys.path.append(PYTHON_ROOT)  # noqa: E402
from rekognition_api.conf import settings  # noqa: E402
from rekognition_api.tests.test_setup import get_test_image  # noqa: E402


with open(TERRAFORM_TFVARS, "r", encoding="utf-8") as f:
    TFVARS = hcl2.load(f)


# pylint: disable=too-many-instance-attributes,too-many-public-methods
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
        self.aws_account_id = os.getenv(key="AWS_ACCOUNT_ID", default=TFVARS["aws_account_id"])
        self.aws_region = os.getenv(key="AWS_REGION", default=TFVARS["aws_region"])
        self.aws_profile = os.getenv(key="AWS_PROFILE", default=None)
        self.shared_resource_identifier = os.getenv(
            key="SHARED_RESOURCE_IDENTIFIER", default=TFVARS["shared_resource_identifier"]
        )
        self.create_custom_domain_name = self.get_create_custom_domain_name()
        self.root_domain = os.getenv(key="ROOT_DOMAIN", default=TFVARS["root_domain"])
        self.domain = self.get_api_domain()
        self.s3_bucket_name = (
            os.getenv(key="S3_BUCKET_NAME") or self.aws_account_id + "-" + self.shared_resource_identifier
        )
        self.api_gateway_name = self.shared_resource_identifier + "-api"

        # aws resources
        self.aws_session = self.get_session()
        self.s3_client = self.aws_session.client("s3")
        self.dynamodb = self.aws_session.client("dynamodb")
        self.api_client = self.aws_session.client("apigateway")

    def get_create_custom_domain_name(self) -> bool:
        """Return the CREATE_CUSTOM_DOMAIN_NAME value."""
        create_custom_domain_name = os.getenv(
            key="CREATE_CUSTOM_DOMAIN_NAME", default=TFVARS["create_custom_domain_name"]
        )
        if isinstance(create_custom_domain_name, bool):
            return create_custom_domain_name

        if isinstance(create_custom_domain_name, str):
            return create_custom_domain_name.lower() in ["true", "1", "yes"]

        return False

    def get_api_domain(self):
        """Return the API domain."""
        if self.create_custom_domain_name:
            return os.getenv(key="DOMAIN") or "api." + self.shared_resource_identifier + "." + self.root_domain

        response = self.api_client.get_rest_apis()
        for item in response["items"]:
            if item["name"] == self.api_gateway_name:
                api_id = item["id"]
                return f"{api_id}.execute-api.{self.aws_region}.amazonaws.com"
        return None

    def get_session(self):
        """Return a new AWS session."""
        if self.aws_profile:
            return boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
        return boto3.Session(region_name=self.aws_region)

    def get_url(self, path):
        """Return the url for the given path."""
        return f"https://{self.domain}{path}"

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
        bucket_prefix = self.s3_bucket_name
        try:
            for bucket in self.s3_client.list_buckets()["Buckets"]:
                if bucket["Name"].startswith(bucket_prefix):
                    return True
            return False
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
            if item["name"] == self.shared_resource_identifier:
                return item["value"]
        return False

    def rekognition_collection_exists(self):
        """Test that the Rekognition collection exists."""
        rekognition_client = self.aws_session.client("rekognition")
        response = rekognition_client.list_collections()
        for collection in response["CollectionIds"]:
            if collection == settings.collection_id:
                return True
        return False

    def test_rekognition_collection_exists(self):
        """Test that the Rekognition collection exists."""
        self.assertTrue(
            self.rekognition_collection_exists(), f"Rekognition collection {settings.collection_id} does not exist."
        )

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
            self.dynamodb_table_exists(self.shared_resource_identifier),
            f"DynamoDB table {self.shared_resource_identifier} does not exist.",
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

    def test_index_endpoint(self):
        """Test that the index endpoint works."""
        filename = "Keanu-Reeves.jpg"
        api_key = self.get_api_keys()
        url = self.get_url(f"/index/{filename}")
        headers = {
            "x-api-key": f"{api_key}",
            "Content-Type": "text/plain",
        }
        data = get_test_image(filename)
        response = requests.put(url, headers=headers, data=data, timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_search_endpoint(self):
        """Test that the search endpoint works."""
        filename = "Keanu-Avril-Mike.jpg"
        api_key = self.get_api_keys()
        url = self.get_url("/search")
        headers = {
            "x-api-key": f"{api_key}",
            "Content-Type": "text/plain",
        }
        data = get_test_image(filename)
        response = requests.put(url, headers=headers, data=data, timeout=5)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        matched_faces = response["matchedFaces"]
        assert "Keanu reeves" in matched_faces, "Keanu reeves not found in matched_faces"
