# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
# pylint: disable=R0801
"""Test Index Lambda function."""

# python stuff
import os
import sys
import unittest


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(HERE))
if PYTHON_ROOT not in sys.path:
    sys.path.append(PYTHON_ROOT)  # noqa: E402

from rekognition_api.conf import settings  # noqa: E402
from rekognition_api.lambda_info import lambda_handler  # noqa: E402

# our stuff
from rekognition_api.tests.test_setup import get_test_file  # noqa: E402


class TestLambdaInfo(unittest.TestCase):
    """Test Index Lambda function."""

    # load a mock lambda_index event

    def setUp(self):
        """Set up test fixtures."""

    def test_get_info(self):
        """Test get_records."""
        dump = lambda_handler({}, {})
        self.assertIsInstance(dump, dict)
        self.assertEqual(dump["statusCode"], 200)
        self.assertEqual(dump["isBase64Encoded"], False)
        self.assertIsInstance(dump["headers"], dict)
        self.assertIsInstance(dump["body"], str)
