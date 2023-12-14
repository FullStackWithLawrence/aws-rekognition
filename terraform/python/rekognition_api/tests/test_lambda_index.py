# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
# pylint: disable=R0801
"""Test Index Lambda function."""

# python stuff
import os
import sys
import unittest


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PYTHON_ROOT)  # noqa: E402

from rekognition_api.exceptions import RekognitionIlligalInvocationError  # noqa: E402
from rekognition_api.lambda_index import (  # noqa: E402
    get_bucket_name,
    get_records,
    validate_event,
)

# our stuff
from rekognition_api.tests.test_setup import get_test_file  # noqa: E402


class TestLambdaIndex(unittest.TestCase):
    """Test Index Lambda function."""

    # load a mock lambda_index event
    event = get_test_file("json/apigateway_index_lambda_event.json")
    event = event["event"]
    response = get_test_file("json/apigateway_index_lambda_response.json")

    def setUp(self):
        """Set up test fixtures."""

    def get_event(self, event):
        """Get the event json from the mock file."""
        return event["event"]

    def test_get_records(self):
        """Test get_records."""
        records = get_records(self.event)
        self.assertEqual(records, self.event["Records"])

    def test_get_bucket_name(self):
        """Test get_bucket_name."""
        bucket_name = get_bucket_name(self.event)
        self.assertEqual(bucket_name, self.event["Records"][0]["s3"]["bucket"]["name"])

    def test_validate_event(self):
        """Test validate_event."""
        event = get_test_file("json/apigateway_index_lambda_event_no_records.json")
        event = self.get_event(event)
        retval = validate_event(event)
        self.assertEqual(retval["statusCode"], 500)

        event = get_test_file("json/apigateway_index_lambda_event_bad_source.json")
        event = self.get_event(event)
        retval = validate_event(event)
        self.assertEqual(retval["statusCode"], 500)

        event = get_test_file("json/apigateway_index_lambda_event_bad_event.json")
        event = self.get_event(event)
        retval = validate_event(event)
        self.assertEqual(retval["statusCode"], 500)
