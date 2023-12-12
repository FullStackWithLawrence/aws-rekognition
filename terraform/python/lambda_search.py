# -*- coding: utf-8 -*-
# pylint: disable=R0801,R0911,R0912,R0914,R0915,W0718
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

from .common import exception_response_factory, http_response_factory
from .conf import cloudwatch_dump, settings


# pylint: disable=unused-argument
def lambda_handler(event, context):  # noqa: C901
    """
    Facial recognition image analysis and search for indexed faces. invoked by API Gateway.
    """
    if settings.debug_mode:
        print(json.dumps(cloudwatch_dump))
        print(json.dumps({"event": event}))

    # all good, lets process the event!
    faces = {}  # Rekognition return value
    matched_faces = []  # any indexed faces found in the Rekognition return value
    try:
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
        image = {"Bytes": image_decoded}

        faces = settings.rekognition_client.search_faces_by_image(
            Image=image,
            CollectionId=settings.collection_id,
            MaxFaces=settings.face_detect_max_faces_count,
            FaceMatchThreshold=settings.face_detect_threshold,
            QualityFilter=settings.face_detect_quality_filter,
        )

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

    # handle anything that went wrong
    # see https://docs.aws.amazon.com/rekognition/latest/dg/error-handling.html
    except settings.rekognition_client.exceptions.InvalidParameterException:
        # If no faces are detected in the image, then index_faces()
        # returns an InvalidParameterException error
        pass

    except (
        settings.rekognition_client.exceptions.ThrottlingException,
        settings.rekognition_client.exceptions.ProvisionedThroughputExceededException,
        settings.rekognition_client.exceptions.ServiceQuotaExceededException,
    ) as e:
        return http_response_factory(status_code=401, body=exception_response_factory(e))

    except settings.rekognition_client.exceptions.AccessDeniedException as e:
        return http_response_factory(status_code=403, body=exception_response_factory(e))

    except settings.rekognition_client.exceptions.ResourceNotFoundException as e:
        return http_response_factory(status_code=404, body=exception_response_factory(e))

    except (
        settings.rekognition_client.exceptions.InvalidS3ObjectException,
        settings.rekognition_client.exceptions.ImageTooLargeException,
        settings.rekognition_client.exceptions.InvalidImageFormatException,
    ) as e:
        return http_response_factory(status_code=406, body=exception_response_factory(e))

    # pylint: disable=broad-except
    except (settings.rekognition_client.exceptions.InternalServerError, Exception) as e:
        return http_response_factory(status_code=500, body=exception_response_factory(e))

    # success!! return the results
    retval = {
        "faces": faces,  # all of the faces that Rekognition found in the image
        "matchedFaces": matched_faces,  # any indexed faces found in DynamoDB
    }
    return http_response_factory(status_code=200, body=retval)
