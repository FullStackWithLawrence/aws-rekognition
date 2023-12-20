# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test Search Lambda function."""

# python stuff
import os
import sys
import unittest


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.append(PYTHON_ROOT)  # noqa: E402

# our stuff
from rekognition_api.conf import settings  # noqa: E402
from rekognition_api.lambda_search import get_faces, get_image_from_event  # noqa: E402
from rekognition_api.tests.test_setup import (  # noqa: E402
    get_test_file,
    get_test_image,
    pack_image_data,
)


class TestLambdaIndex(unittest.TestCase):
    """Test Search Lambda function."""

    image_filename = "Keanu-Reeves.jpg"
    image = get_test_image(filename=image_filename)
    image_packed = pack_image_data(filename=image_filename)

    # load a mock lambda_index event
    search_event = get_test_file("json/apigateway_search_lambda_event.json")
    index_event = get_test_file("json/apigateway_index_lambda_event.json")
    response = get_test_file("json/apigateway_search_lambda_response.json")
    dynamodb_records = get_test_file("json/dynamodb-sample-records.json")
    rekognition_search_output = get_test_file("json/rekognition_search_output.json")

    def setUp(self):
        """Set up test fixtures."""

    def test_get_image_from_event(self):
        """Test get_image_from_event."""
        #     image_from_event = get_image_from_event(self.search_event)

        #     self.assertEqual(image_from_event, self.image)
        print("Not implemented")
        assert True

    def test_get_faces(self):
        """Test get_faces."""
        # faces = settings.rekognition_client.search_faces_by_image(
        #     Image=self.image_packed,
        #     CollectionId=settings.aws_rekognition_collection_id,
        #     MaxFaces=settings.aws_rekognition_face_detect_max_faces_count,
        #     FaceMatchThreshold=settings.aws_rekognition_face_detect_threshold,
        #     QualityFilter=settings.aws_rekognition_face_detect_quality_filter,
        # )
        # faces = get_faces(self.image_packed)
        print("Not implemented")
        assert True
