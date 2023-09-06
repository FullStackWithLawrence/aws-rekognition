# ------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date:       sep-2023
#
# usage:      AWS Lambda to process jpeg image files uploaded to S3.
#
#             For a given input image, first detects the largest face in the image,
#             and then searches the specified collection for matching faces.
#             The operation compares the features of the input face with faces in the specified collection.
#
#             The response returns an array of faces that match, ordered by similarity
#             score with the highest similarity first. More specifically, it is an
#             array of metadata for each face match found. Along with the metadata,
#             the response also includes a similarity indicating how similar the face
#             is to the input face. In the response, the operation also returns the
#             bounding box (and a confidence level that the bounding box contains a face)
#             of the face that Amazon Rekognition used for the input image.
#
# Notes:      The image must be either a PNG or JPEG formatted file.
#
#
# OFFICIAL DOCUMENTATION:
#             https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition/client/search_faces_by_image.html
#             https://docs.aws.amazon.com/rekognition_client/latest/dg/example_rekognition_Usage_FindFacesInCollection_section.html
#
# GISTS: https://gist.github.com/alexcasalboni/0f21a1889f09760f8981b643326730ff
# ------------------------------------------------------------------------------
import os  # utilities for interacting with the operating system
import boto3  # AWS SDK for Python https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

MAX_FACES = int(os.environ["MAX_FACES_COUNT"])
THRESHOLD = float(os.environ["FACE_DETECT_THRESHOLD"])
QUALITY_FILTER = os.environ["QUALITY_FILTER"]
TABLE_ID = os.environ["TABLE_ID"]
AWS_REGION = os.environ["REGION"]
COLLECTION_ID = os.environ["COLLECTION_ID"]
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")

rekognition_client = boto3.client("rekognition", AWS_REGION)

dynamodb_client = boto3.resource("dynamodb")
dynamodb_table = dynamodb_client.Table(TABLE_ID)


def lambda_handler(event, context):
    faces = {}  # Rekognition return value
    matched_faces = []  # any indexed faces found in the Rekognition return value
    try:
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
        image = {"Bytes": event["image"].encode()}
        faces = rekognition_client.search_faces_by_image(
            Image=image,
            CollectionId=COLLECTION_ID,
            MaxFaces=MAX_FACES,
            FaceMatchThreshold=THRESHOLD,
            QualityFilter=QUALITY_FILTER,
        )

        # ----------------------------------------------------------------------
        # return structure: doc/rekogition_search_faces_by_image.json
        # ----------------------------------------------------------------------
        for face in faces["FaceMatches"]:
            item = dynamodb_table.get_item(Key={"FaceId": face["Face"]["FaceId"]})
            if "Item" in item:
                matched_faces.append(item["Item"]["object_metadata"])

    except rekognition_client.exceptions.InvalidS3ObjectException:
        print("ERROR: InvalidS3ObjectException")
        return {"statusCode": 406, "data": None}
    except rekognition_client.exceptions.InvalidParameterException:
        # If no faces are detected in the input image, SearchFacesByImage returns an InvalidParameterException error
        pass
    except rekognition_client.exceptions.ImageTooLargeException:
        print("ERROR: ImageTooLargeException")
        return {"statusCode": 406, "data": None}
    except rekognition_client.exceptions.AccessDeniedException:
        print("ERROR: AccessDeniedException")
        return {"statusCode": 403, "data": None}
    except rekognition_client.exceptions.InternalServerError:
        print("ERROR: InternalServerError")
        return {"statusCode": 500, "data": None}
    except rekognition_client.exceptions.ThrottlingException:
        print("ERROR: ThrottlingException")
        return {"statusCode": 401, "data": None}
    except rekognition_client.exceptions.ProvisionedThroughputExceededException:
        print("ERROR: ProvisionedThroughputExceededException")
        return {"statusCode": 401, "data": None}
    except rekognition_client.exceptions.ResourceNotFoundException:
        print("ERROR: ResourceNotFoundException")
        return {"statusCode": 404, "data": None}
    except rekognition_client.exceptions.InvalidImageFormatException:
        print("ERROR: InvalidImageFormatException")
        return {"statusCode": 406, "data": None}
    except Exception as e:
        raise e

    retval = {
        "faces": faces,  # all of the faces that Rekognition found in the image
        "matchedFaces": matched_faces,  # any indexed faces found in DynamoDB
    }
    return {"statusCode": 200, "data": retval}
