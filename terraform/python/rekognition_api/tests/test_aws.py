# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test configuration Settings class."""

import inspect

# python stuff
import os
import sys
import unittest

# 3rd party stuff
import requests
from dotenv import load_dotenv


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(HERE))
if PYTHON_ROOT not in sys.path:
    sys.path.append(PYTHON_ROOT)  # noqa: E402

# our stuff
from rekognition_api.aws import aws_infrastructure_config as aws_config  # noqa: E402
from rekognition_api.conf import Services, settings  # noqa: E402
from rekognition_api.tests.test_setup import get_test_image  # noqa: E402


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

    def test_rekognition_collection_exists(self):
        """Test that the Rekognition collection exists."""
        if not Services.enabled(Services.AWS_REKOGNITION):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        self.assertTrue(
            aws_config.rekognition_collection_exists(),
            f"Rekognition collection {settings.aws_rekognition_collection_id} does not exist.",
        )

    def test_aws_connection_works(self):
        """Test that the AWS connection works."""
        if not Services.enabled(Services.AWS_CLI):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        self.assertTrue(aws_config.aws_connection_works(), "AWS connection failed.")

    def test_domain_exists(self):
        """Test that settings handles missing .env values."""
        self.assertTrue(aws_config.domain_exists(), f"Domain {settings.aws_apigateway_domain_name} does not exist.")

    def test_bucket_exists(self):
        """Test that the S3 bucket exists."""
        if not Services.enabled(Services.AWS_S3):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        bucket_prefix = settings.aws_s3_bucket_name
        self.assertTrue(aws_config.bucket_exists(bucket_prefix), f"S3 bucket {bucket_prefix} does not exist.")

    def test_dynamodb_table_exists(self):
        """Test that the DynamoDB table exists."""
        if not Services.enabled(Services.AWS_DYNAMODB):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        self.assertTrue(
            aws_config.dynamodb_table_exists(settings.shared_resource_identifier),
            f"DynamoDB table {settings.shared_resource_identifier} does not exist.",
        )

    def test_api_exists(self):
        """Test that the API Gateway exists."""
        if not Services.enabled(Services.AWS_APIGATEWAY):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        api = aws_config.get_api(settings.aws_apigateway_name)
        self.assertIsInstance(api, dict, "API Gateway does not exist.")

    def test_api_resource_index_exists(self):
        """Test that the API Gateway index resource exists."""
        if not Services.enabled(Services.AWS_APIGATEWAY):
            return
        self.assertTrue(
            aws_config.api_resource_and_method_exists("/index/{filename}", "PUT"),
            "API Gateway index (PUT) resource does not exist.",
        )

    def test_api_resource_search_exists(self):
        """Test that the API Gateway index resource exists."""
        if not Services.enabled(Services.AWS_APIGATEWAY):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        self.assertTrue(
            aws_config.api_resource_and_method_exists("/search", "ANY"),
            "API Gateway search (ANY) resource does not exist.",
        )

    def test_api_key_exists(self):
        """Test that an API key exists."""
        if not Services.enabled(Services.AWS_APIGATEWAY):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        api_key = aws_config.get_api_keys()
        self.assertIsInstance(api_key, str, "API key does not exist.")
        self.assertGreaterEqual(len(api_key), 15, "API key is too short.")

    def test_index_endpoint(self):
        """Test that the index endpoint works."""
        if not Services.enabled(Services.AWS_APIGATEWAY):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        filename = "Keanu-Reeves.jpg"
        api_key = aws_config.get_api_keys()
        url = aws_config.get_url(f"/index/{filename}")
        headers = {
            "x-api-key": f"{api_key}",
            "Content-Type": "text/plain",
        }
        data = get_test_image(filename)
        response = requests.put(url, headers=headers, data=data, timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_search_endpoint(self):
        """Test that the search endpoint works."""
        if not Services.enabled(Services.AWS_APIGATEWAY):
            print("skipping: ", inspect.currentframe().f_code.co_name)
            return
        filename = "Keanu-Avril-Mike.jpg"
        api_key = aws_config.get_api_keys()
        url = aws_config.get_url("/search")
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
