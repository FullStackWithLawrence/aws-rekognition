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
sys.path.append(PYTHON_ROOT)  # noqa: E402

# our stuff
from rekognition_api.conf import Settings, SettingsDefaults  # noqa: E402
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
        self.assertEqual(mock_settings.table_id, SettingsDefaults.TABLE_ID)
        self.assertEqual(mock_settings.collection_id, SettingsDefaults.COLLECTION_ID)
        self.assertEqual(mock_settings.face_detect_max_faces_count, SettingsDefaults.FACE_DETECT_MAX_FACES_COUNT)
        self.assertEqual(mock_settings.face_detect_attributes, SettingsDefaults.FACE_DETECT_ATTRIBUTES)
        self.assertEqual(mock_settings.face_detect_quality_filter, SettingsDefaults.FACE_DETECT_QUALITY_FILTER)
        self.assertEqual(mock_settings.face_detect_threshold, SettingsDefaults.FACE_DETECT_THRESHOLD)

    def test_env_nulls(self):
        """Test that settings handles missing .env values."""
        os.environ.clear()
        env_path = self.env_path(".env.test_nulls")
        loaded = load_dotenv(env_path)
        self.assertTrue(loaded)

        mock_settings = Settings()

        self.assertEqual(mock_settings.aws_region, SettingsDefaults.AWS_REGION)
        self.assertEqual(mock_settings.table_id, SettingsDefaults.TABLE_ID)
        self.assertEqual(mock_settings.collection_id, SettingsDefaults.COLLECTION_ID)
        self.assertEqual(mock_settings.face_detect_max_faces_count, SettingsDefaults.FACE_DETECT_MAX_FACES_COUNT)
        self.assertEqual(mock_settings.face_detect_attributes, SettingsDefaults.FACE_DETECT_ATTRIBUTES)
        self.assertEqual(mock_settings.face_detect_quality_filter, SettingsDefaults.FACE_DETECT_QUALITY_FILTER)
        self.assertEqual(mock_settings.face_detect_threshold, SettingsDefaults.FACE_DETECT_THRESHOLD)

    def test_env_overrides(self):
        """Test that settings takes custom .env values."""
        os.environ.clear()
        env_path = self.env_path(".env.test_01")
        loaded = load_dotenv(env_path)
        self.assertTrue(loaded)

        mock_settings = Settings()

        self.assertEqual(mock_settings.aws_region, "us-west-1")
        self.assertEqual(mock_settings.table_id, "TEST_facialrecognition")
        self.assertEqual(mock_settings.collection_id, "TEST_facialrecognition-collection")
        self.assertEqual(mock_settings.face_detect_max_faces_count, 100)
        self.assertEqual(mock_settings.face_detect_attributes, "TEST_DEFAULT")
        self.assertEqual(mock_settings.face_detect_quality_filter, "TEST_AUTO")
        self.assertEqual(mock_settings.face_detect_threshold, 100)
        self.assertEqual(mock_settings.debug_mode, True)

    @patch.dict(os.environ, {"AWS_REGION": "invalid-region"})
    def test_invalid_aws_region_code(self):
        """Test that Pydantic raises a validation error for environment variable with non-existent aws region code."""

        with self.assertRaises(RekognitionValueError):
            Settings()

    @patch.dict(os.environ, {"FACE_DETECT_MAX_FACES_COUNT": "-1"})
    def test_invalid_max_faces_count(self):
        """Test that Pydantic raises a validation error for environment variable w negative integer values."""

        with self.assertRaises(PydanticValidationError):
            Settings()

    @patch.dict(os.environ, {"FACE_DETECT_THRESHOLD": "-1"})
    def test_invalid_threshold(self):
        """Test that Pydantic raises a validation error for environment variable w negative integer values."""

        with self.assertRaises(PydanticValidationError):
            Settings()

    def test_configure_with_class_constructor(self):
        """test that we can set values with the class constructor"""

        mock_settings = Settings(
            aws_region="eu-west-1",
            table_id="TEST_facialrecognition",
            collection_id="TEST_facialrecognition-collection",
            face_detect_max_faces_count=101,
            face_detect_attributes="TEST_DEFAULT",
            face_detect_quality_filter="TEST_AUTO",
            face_detect_threshold=102,
            debug_mode=True,
        )

        self.assertEqual(mock_settings.aws_region, "eu-west-1")
        self.assertEqual(mock_settings.table_id, "TEST_facialrecognition")
        self.assertEqual(mock_settings.collection_id, "TEST_facialrecognition-collection")
        self.assertEqual(mock_settings.face_detect_max_faces_count, 101)
        self.assertEqual(mock_settings.face_detect_attributes, "TEST_DEFAULT")
        self.assertEqual(mock_settings.face_detect_quality_filter, "TEST_AUTO")
        self.assertEqual(mock_settings.face_detect_threshold, 102)
        self.assertEqual(mock_settings.debug_mode, True)

    def test_configure_neg_int_with_class_constructor(self):
        """test that we cannot set negative int values with the class constructor"""

        with self.assertRaises(PydanticValidationError):
            Settings(face_detect_max_faces_count=-1)

        with self.assertRaises(PydanticValidationError):
            Settings(face_detect_threshold=-1)

    def test_readonly_settings(self):
        """test that we can't set readonly values with the class constructor"""

        mock_settings = Settings(aws_region="eu-west-1")
        with self.assertRaises(PydanticValidationError):
            mock_settings.aws_region = "us-west-1"

        with self.assertRaises(PydanticValidationError):
            mock_settings.table_id = "TEST_facialrecognition"

        with self.assertRaises(PydanticValidationError):
            mock_settings.collection_id = "TEST_facialrecognition-collection"

        with self.assertRaises(PydanticValidationError):
            mock_settings.face_detect_attributes = "TEST_DEFAULT"

        with self.assertRaises(PydanticValidationError):
            mock_settings.face_detect_quality_filter = "TEST_AUTO"

        with self.assertRaises(PydanticValidationError):
            mock_settings.debug_mode = True

        with self.assertRaises(PydanticValidationError):
            mock_settings.face_detect_max_faces_count = 25

        with self.assertRaises(PydanticValidationError):
            mock_settings.face_detect_threshold = 25

    def test_cloudwatch_dump(self):
        """Test that cloudwatch_dump is a dict."""

        mock_settings = Settings()
        self.assertIsInstance(mock_settings.cloudwatch_dump, dict)

    def test_cloudwatch_dump_keys(self):
        """Test that cloudwatch_dump contains the expected keys."""

        environment = Settings().cloudwatch_dump["environment"]
        self.assertIn("os", environment)
        self.assertIn("system", environment)
        self.assertIn("release", environment)
        self.assertIn("boto3", environment)
        self.assertIn("COLLECTION_ID", environment)
        self.assertIn("TABLE_ID", environment)
        self.assertIn("MAX_FACES", environment)
        self.assertIn("FACE_DETECT_ATTRIBUTES", environment)
        self.assertIn("QUALITY_FILTER", environment)
        self.assertIn("DEBUG_MODE", environment)

    def test_cloudwatch_values(self):
        """Test that cloudwatch_dump contains the expected values."""

        mock_settings = Settings()
        environment = mock_settings.cloudwatch_dump["environment"]

        self.assertEqual(environment["COLLECTION_ID"], mock_settings.collection_id)
        self.assertEqual(environment["TABLE_ID"], mock_settings.table_id)
        self.assertEqual(environment["MAX_FACES"], mock_settings.face_detect_max_faces_count)
        self.assertEqual(environment["FACE_DETECT_ATTRIBUTES"], mock_settings.face_detect_attributes)
        self.assertEqual(environment["QUALITY_FILTER"], mock_settings.face_detect_quality_filter)
        self.assertEqual(environment["DEBUG_MODE"], mock_settings.debug_mode)
