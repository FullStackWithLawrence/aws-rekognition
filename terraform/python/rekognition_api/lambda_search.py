# -*- coding: utf-8 -*-
# pylint: disable=R0911,R0912,W0718,R0801
"""
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date:       sep-2023
#
# Rekognition.search_faces_by_image()
# ------------------------------------
# For a given input image, first detects the largest face in the image,
# and then searches the specified collection for matching faces.
# The operation compares the features of the input face with faces in the specified collection.
#
# The response returns an array of faces that match, ordered by similarity
# score with the highest similarity first. More specifically, it is an
# array of metadata for each face match found. Along with the metadata,
# the response also includes a similarity indicating how similar the face
# is to the input face. In the response, the operation also returns the
# bounding box (and a confidence level that the bounding box contains a face)
# of the face that Amazon Rekognition used for the input image.
#
# Notes:
# - incoming image file is base64 encoded.
#   see https://code.tutsplus.com/base64-encoding-and-decoding-using-python--cms-25588t
#
# - The image must be either a PNG or JPEG formatted file.
#
# OFFICIAL DOCUMENTATION:
# - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition/client/search_faces_by_image.html
# - https://docs.aws.amazon.com/settings.rekognition_client/latest/dg/example_rekognition_Usage_FindFacesInCollection_section.html
#
# GISTS:
# - https://gist.github.com/alexcasalboni/0f21a1889f09760f8981b643326730ff
"""

import base64  # library with base63 encoding/decoding functions
import json  # library for interacting with JSON data https://www.json.org/json-en.html

from rekognition_api.conf import settings
from rekognition_api.exceptions import EXCEPTION_MAP
from rekognition_api.utils import (
    cloudwatch_handler,
    exception_response_factory,
    http_response_factory,
)


def get_image_from_event(event):
    """extract and decode the raw image data from the event"""
    # see
    #  - https://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character-u-xa0-in-position-20
    #  - line 39, in _bytes_from_decode_data ValueError: string argument should contain only ASCII characters
    #  - https://stackoverflow.com/questions/53340627/typeerror-expected-bytes-like-object-not-str
    #  - alternate syntax: image_raw = ''.join(image_raw).encode('ascii').strip()
    image_raw = str(event["body"]).encode("ascii")
    image_decoded = base64.b64decode(image_raw)

    # https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal
    # Image: base64-encoded bytes or an S3 object.
    # Image={
    #     'Bytes': b'bytes',
    #     'S3Object': {
    #         'Bucket': 'string',
    #         'Name': 'string',
    #         'Version': 'string'
    #     }
    # },
    return {"Bytes": image_decoded}


def get_faces(image):
    """return a list of faces found in the image"""
    return settings.aws_rekognition_client.search_faces_by_image(
        Image=image,
        CollectionId=settings.aws_rekognition_collection_id,
        MaxFaces=settings.aws_rekognition_face_detect_max_faces_count,
        FaceMatchThreshold=settings.aws_rekognition_face_detect_threshold,
        QualityFilter=settings.aws_rekognition_face_detect_quality_filter,
    )


def get_matched_faces(faces):
    """return a list of matched faces"""
    matched_faces = []  # any indexed faces found in the Rekognition return value
    # ----------------------------------------------------------------------
    # return structure: doc/rekogition_search_faces_by_image.json
    # ----------------------------------------------------------------------
    for face in faces["FaceMatches"]:
        item = settings.dynamodb_table.get_item(Key={"FaceId": face["Face"]["FaceId"]})
        if "Item" in item:
            matched = (
                str(item["Item"]["ExternalImageId"])
                .replace("-", " ")
                .replace("_", " ")
                .replace(".jpg", "")
                .replace(".png", "")
                .capitalize()
            )
            matched_faces.append(matched)

    return matched_faces


# pylint: disable=unused-argument
def lambda_handler(event, context):  # noqa: C901
    """
    Facial recognition image analysis and search for indexed faces. invoked by API Gateway.
    """
    cloudwatch_handler(event, settings.dump, debug_mode=settings.debug_mode)
    try:
        image = get_image_from_event(event)
        faces = get_faces(image)
        matched_faces = get_matched_faces(faces)

        retval = {
            "faces": faces,  # all of the faces that Rekognition found in the image
            "matchedFaces": matched_faces,  # any indexed faces found in DynamoDB
        }

    # handle anything that went wrong
    # see https://docs.aws.amazon.com/rekognition/latest/dg/error-handling.html
    except settings.aws_rekognition_client.exceptions.InvalidParameterException:
        # If no faces are detected in the image, then index_faces()
        # returns an InvalidParameterException error
        pass

    except Exception as e:
        status_code, _message = EXCEPTION_MAP.get(type(e), (500, "Internal server error"))
        return http_response_factory(status_code=status_code, body=exception_response_factory(e))

    return http_response_factory(status_code=200, body=retval)
