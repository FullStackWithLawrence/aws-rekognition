# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test configuration Settings class."""

# python stuff
import os
import sys
import time
import unittest


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(HERE))
if PYTHON_ROOT not in sys.path:
    sys.path.append(PYTHON_ROOT)  # noqa: E402

# our stuff
from rekognition_api.conf import Settings  # noqa: E402


class TestConfigurationDump(unittest.TestCase):
    """Test configuration."""

    def test_dump(self):
        """Test that dump is a dict."""

        mock_settings = Settings(aws_region="us-east-1")
        self.assertIsInstance(mock_settings.dump, dict)

    def test_dump_keys(self):
        """Test that dump contains the expected keys."""

        mock_settings = Settings(aws_region="us-east-1")

        dump = mock_settings.dump
        self.assertIn("environment", dump)
        self.assertIn("aws_auth", dump)
        self.assertIn("aws_rekognition", dump)
        self.assertIn("aws_dynamodb", dump)
        self.assertIn("aws_s3", dump)
        self.assertIn("aws_apigateway", dump)
        self.assertIn("terraform", dump)

    def test_dump_values(self):
        """Test that dump contains the expected values."""

        mock_settings = Settings(aws_region="us-east-1")
        environment = mock_settings.dump["environment"]

        self.assertEqual(environment["is_using_tfvars_file"], mock_settings.is_using_tfvars_file)
        self.assertEqual(environment["is_using_dotenv_file"], mock_settings.is_using_dotenv_file)
        self.assertEqual(environment["is_using_aws_rekognition"], mock_settings.is_using_aws_rekognition)
        self.assertEqual(environment["is_using_aws_dynamodb"], mock_settings.is_using_aws_dynamodb)
        self.assertEqual(environment["shared_resource_identifier"], mock_settings.shared_resource_identifier)
        self.assertEqual(environment["debug_mode"], mock_settings.debug_mode)
        self.assertEqual(environment["dump_defaults"], mock_settings.dump_defaults)
        self.assertEqual(environment["version"], mock_settings.version)
