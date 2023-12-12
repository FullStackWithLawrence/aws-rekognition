# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Simple test bank."""
import os
import sys
import unittest

from dotenv import load_dotenv


PYTHON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PYTHON_ROOT)  # noqa: E402


from rekognition_api.conf import Settings, SettingsDefaults  # noqa: E402


class TestConfiguration(unittest.TestCase):
    """Test configuration.""" ""

    def setUp(self):
        """Set up test fixtures."""
        load_dotenv(".env.test")
        self.mock_settings = Settings()

    def test_defaults(self):
        """Test that settings == SettingsDefaults when no .env is in use."""
        self.assertEqual(self.mock_settings.aws_region, SettingsDefaults.AWS_REGION)
        self.assertEqual(self.mock_settings.table_id, SettingsDefaults.TABLE_ID)
        self.assertEqual(self.mock_settings.collection_id, SettingsDefaults.COLLECTION_ID)
        self.assertEqual(self.mock_settings.face_detect_max_faces_count, SettingsDefaults.FACE_DETECT_MAX_FACES_COUNT)
        self.assertEqual(self.mock_settings.face_detect_attributes, SettingsDefaults.FACE_DETECT_ATTRIBUTES)
        self.assertEqual(self.mock_settings.face_detect_quality_filter, SettingsDefaults.FACE_DETECT_QUALITY_FILTER)
        self.assertEqual(self.mock_settings.face_detect_threshold, SettingsDefaults.FACE_DETECT_THRESHOLD)
