# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test configuration Settings class."""

# python stuff
import os
import sys
import unittest
from unittest.mock import patch

# 3rd party stuff
from dotenv import load_dotenv
from pydantic_core import ValidationError as PydanticValidationError


PYTHON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
if PYTHON_ROOT not in sys.path:
    sys.path.append(PYTHON_ROOT)  # noqa: E402

# our stuff
from rekognition_api.conf import Settings, SettingsDefaults  # noqa: E402
from rekognition_api.const import TFVARS  # noqa: E402
from rekognition_api.exceptions import RekognitionValueError  # noqa: E402


class TestConfiguration(unittest.TestCase):
    """Test configuration."""

    # Get the directory of the current script
    here = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        """Set up test fixtures."""

    def env_path(self, filename):
        """Return the path to the .env file."""
        return os.path.join(self.here, filename)

    def test_conf_defaults(self):
        """Test that settings == SettingsDefaults when no .env is in use."""
        os.environ.clear()
        mock_settings = Settings()

        self.assertEqual(mock_settings.aws_region, SettingsDefaults.AWS_REGION)
        self.assertEqual(mock_settings.aws_dynamodb_table_id, SettingsDefaults.AWS_DYNAMODB_TABLE_ID)
        self.assertEqual(mock_settings.aws_rekognition_collection_id, SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID)
        self.assertEqual(
            mock_settings.aws_rekognition_face_detect_max_faces_count,
            SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT,
        )
        self.assertEqual(
            mock_settings.aws_rekognition_face_detect_attributes,
            SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES,
        )
        self.assertEqual(
            mock_settings.aws_rekognition_face_detect_quality_filter,
            SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER,
        )
        self.assertEqual(
            mock_settings.aws_rekognition_face_detect_threshold, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD
        )

    def test_env_illegal_nulls(self):
        """Test that settings handles missing .env values."""
        os.environ.clear()
        env_path = self.env_path(".env.test_illegal_nulls")
        loaded = load_dotenv(env_path)
        self.assertTrue(loaded)

        with self.assertRaises(PydanticValidationError):
            Settings()

    def test_env_nulls(self):
        """Test that settings handles missing .env values."""
        os.environ.clear()
        env_path = self.env_path(".env.test_legal_nulls")
        loaded = load_dotenv(env_path)
        self.assertTrue(loaded)

        mock_settings = Settings()

        self.assertEqual(mock_settings.aws_region, SettingsDefaults.AWS_REGION)
        self.assertEqual(mock_settings.aws_dynamodb_table_id, SettingsDefaults.AWS_DYNAMODB_TABLE_ID)
        self.assertEqual(mock_settings.aws_rekognition_collection_id, SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID)
        self.assertEqual(
            mock_settings.aws_rekognition_face_detect_attributes,
            SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES,
        )
        self.assertEqual(
            mock_settings.aws_rekognition_face_detect_quality_filter,
            SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER,
        )

    def test_env_overrides(self):
        """Test that settings takes custom .env values."""
        os.environ.clear()
        env_path = self.env_path(".env.test_01")
        loaded = load_dotenv(env_path)
        self.assertTrue(loaded)

        mock_settings = Settings()

        self.assertEqual(mock_settings.aws_region, "us-west-1")
        self.assertEqual(mock_settings.aws_dynamodb_table_id, "TEST_facialrecognition")
        self.assertEqual(mock_settings.aws_rekognition_collection_id, "TEST_facialrecognition-collection")
        self.assertEqual(mock_settings.aws_rekognition_face_detect_max_faces_count, 100)
        self.assertEqual(mock_settings.aws_rekognition_face_detect_attributes, "TEST_DEFAULT")
        self.assertEqual(mock_settings.aws_rekognition_face_detect_quality_filter, "TEST_AUTO")
        self.assertEqual(mock_settings.aws_rekognition_face_detect_threshold, 100)
        self.assertEqual(mock_settings.debug_mode, True)

    @patch.dict(
        os.environ,
        {"AWS_PROFILE": "TEST_PROFILE", "AWS_ACCESS_KEY_ID": "TEST_KEY", "AWS_SECRET_ACCESS_KEY": "TEST_SECRET"},
    )
    def test_aws_credentials_with_profile(self):
        """Test that key and secret are unset when using profile."""

        mock_settings = Settings()
        self.assertEqual(mock_settings.aws_access_key_id_source, "aws_profile")
        self.assertEqual(mock_settings.aws_secret_access_key_source, "aws_profile")

    @patch.dict(
        os.environ, {"AWS_PROFILE": "", "AWS_ACCESS_KEY_ID": "TEST_KEY", "AWS_SECRET_ACCESS_KEY": "TEST_SECRET"}
    )
    def test_aws_credentials_without_profile(self):
        """Test that key and secret are unset when using profile."""

        mock_settings = Settings()
        # pylint: disable=no-member
        self.assertEqual(mock_settings.aws_access_key_id.get_secret_value(), "TEST_KEY")
        # pylint: disable=no-member
        self.assertEqual(mock_settings.aws_secret_access_key.get_secret_value(), "TEST_SECRET")
        self.assertEqual(mock_settings.aws_access_key_id_source, "environ")
        self.assertEqual(mock_settings.aws_secret_access_key_source, "environ")

    def test_aws_credentials_noinfo(self):
        """Test that key and secret are unset when using profile."""
        os.environ.clear()
        mock_settings = Settings()
        aws_profile = TFVARS.get("aws_profile", None)
        self.assertEqual(mock_settings.aws_profile, aws_profile)
        # pylint: disable=no-member
        self.assertEqual(mock_settings.aws_access_key_id.get_secret_value(), None)
        # pylint: disable=no-member
        self.assertEqual(mock_settings.aws_secret_access_key.get_secret_value(), None)
        self.assertEqual(mock_settings.aws_access_key_id_source, "unset")
        self.assertEqual(mock_settings.aws_secret_access_key_source, "unset")

    @patch.dict(os.environ, {"AWS_REGION": "invalid-region"})
    def test_invalid_aws_region_code(self):
        """Test that Pydantic raises a validation error for environment variable with non-existent aws region code."""

        with self.assertRaises(RekognitionValueError):
            Settings()

    @patch.dict(os.environ, {"AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT": "-1"})
    def test_invalid_max_faces_count(self):
        """Test that Pydantic raises a validation error for environment variable w negative integer values."""

        with self.assertRaises(PydanticValidationError):
            Settings()

    @patch.dict(os.environ, {"AWS_REKOGNITION_FACE_DETECT_THRESHOLD": "-1"})
    def test_invalid_threshold(self):
        """Test that Pydantic raises a validation error for environment variable w negative integer values."""

        with self.assertRaises(PydanticValidationError):
            Settings()

    def test_configure_with_class_constructor(self):
        """test that we can set values with the class constructor"""

        mock_settings = Settings(
            aws_region="eu-west-1",
            aws_dynamodb_table_id="TEST_facialrecognition",
            aws_rekognition_collection_id="TEST_facialrecognition-collection",
            aws_rekognition_face_detect_max_faces_count=101,
            aws_rekognition_face_detect_attributes="TEST_DEFAULT",
            aws_rekognition_face_detect_quality_filter="TEST_AUTO",
            aws_rekognition_face_detect_threshold=102,
            debug_mode=True,
        )

        self.assertEqual(mock_settings.aws_region, "eu-west-1")
        self.assertEqual(mock_settings.aws_dynamodb_table_id, "TEST_facialrecognition")
        self.assertEqual(mock_settings.aws_rekognition_collection_id, "TEST_facialrecognition-collection")
        self.assertEqual(mock_settings.aws_rekognition_face_detect_max_faces_count, 101)
        self.assertEqual(mock_settings.aws_rekognition_face_detect_attributes, "TEST_DEFAULT")
        self.assertEqual(mock_settings.aws_rekognition_face_detect_quality_filter, "TEST_AUTO")
        self.assertEqual(mock_settings.aws_rekognition_face_detect_threshold, 102)
        self.assertEqual(mock_settings.debug_mode, True)

    def test_configure_neg_int_with_class_constructor(self):
        """test that we cannot set negative int values with the class constructor"""

        with self.assertRaises(PydanticValidationError):
            Settings(aws_rekognition_face_detect_max_faces_count=-1)

        with self.assertRaises(PydanticValidationError):
            Settings(aws_rekognition_face_detect_threshold=-1)

    def test_readonly_settings(self):
        """test that we can't set readonly values with the class constructor"""

        mock_settings = Settings(aws_region="eu-west-1")
        with self.assertRaises(PydanticValidationError):
            mock_settings.aws_region = "us-west-1"

        with self.assertRaises(PydanticValidationError):
            mock_settings.aws_dynamodb_table_id = "TEST_facialrecognition"

        with self.assertRaises(PydanticValidationError):
            mock_settings.aws_rekognition_collection_id = "TEST_facialrecognition-collection"

        with self.assertRaises(PydanticValidationError):
            mock_settings.aws_rekognition_face_detect_attributes = "TEST_DEFAULT"

        with self.assertRaises(PydanticValidationError):
            mock_settings.aws_rekognition_face_detect_quality_filter = "TEST_AUTO"

        with self.assertRaises(PydanticValidationError):
            mock_settings.debug_mode = True

        with self.assertRaises(PydanticValidationError):
            mock_settings.aws_rekognition_face_detect_max_faces_count = 25

        with self.assertRaises(PydanticValidationError):
            mock_settings.aws_rekognition_face_detect_threshold = 25

    def test_dump(self):
        """Test that dump is a dict."""

        mock_settings = Settings()
        self.assertIsInstance(mock_settings.dump, dict)

    def test_dump_keys(self):
        """Test that dump contains the expected keys."""

        dump = Settings().dump
        self.assertIn("environment", dump)
        self.assertIn("aws_auth", dump)
        self.assertIn("aws_rekognition", dump)
        self.assertIn("aws_dynamodb", dump)
        self.assertIn("aws_s3", dump)
        self.assertIn("aws_apigateway", dump)
        self.assertIn("terraform", dump)

    def test_dump_values(self):
        """Test that dump contains the expected values."""

        mock_settings = Settings()
        environment = mock_settings.dump["environment"]

        self.assertEqual(environment["is_using_tfvars_file"], mock_settings.is_using_tfvars_file)
        self.assertEqual(environment["is_using_dotenv_file"], mock_settings.is_using_dotenv_file)
        self.assertEqual(environment["is_using_aws_rekognition"], mock_settings.is_using_aws_rekognition)
        self.assertEqual(environment["is_using_aws_dynamodb"], mock_settings.is_using_aws_dynamodb)
        self.assertEqual(environment["shared_resource_identifier"], mock_settings.shared_resource_identifier)
        self.assertEqual(environment["debug_mode"], mock_settings.debug_mode)
        self.assertEqual(environment["dump_defaults"], mock_settings.dump_defaults)
        self.assertEqual(environment["version"], mock_settings.version)
