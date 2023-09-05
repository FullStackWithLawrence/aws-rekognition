#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
import os
import boto3

MAX_FACES = int(os.environ["MAX_FACES_COUNT"])
THRESHOLD = float(os.environ["FACE_DETECT_THRESHOLD"])
QUALITY_FILTER = os.environ["QUALITY_FILTER"]
TABLE_ID = os.environ["TABLE_ID"]
AWS_REGION = os.environ["AWS_REGION"]

rekognition_client = boto3.client("rekognition", AWS_REGION)

dynamodb_client = boto3.resource('dynamodb')
dynamodb_table = dynamodb_client.Table(TABLE_ID)

def lambda_handler(event, context):
    try:
        # Image: base64-encoded bytes or an S3 object.
        # Image={
        #     'Bytes': b'bytes',
        #     'S3Object': {
        #         'Bucket': 'string',
        #         'Name': 'string',
        #         'Version': 'string'
        #     }
        # },

        image = {'Bytes': event['image'].encode()}
        faces = rekognition_client.search_faces_by_image(
            CollectionId='string',
            Image=image,
            MaxFaces=MAX_FACES,
            FaceMatchThreshold=THRESHOLD,
            QualityFilter=QUALITY_FILTER
        )
        #return faces['FaceMatches']

        #----------------------------------------------------------------------
        # expected return structure
        #----------------------------------------------------------------------
        # {
        #     'SearchedFaceBoundingBox': {
        #         'Width': ...,
        #         'Height': ...,
        #         'Left': ...,
        #         'Top': ...
        #     },
        #     'SearchedFaceConfidence': ...,
        #     'FaceMatches': [
        #         {
        #             'Similarity': ...,
        #             'Face': {
        #                 'FaceId': 'string',
        #                 'BoundingBox': {
        #                     'Width': ...,
        #                     'Height': ...,
        #                     'Left': ...,
        #                     'Top': ...
        #                 },
        #                 'ImageId': 'string',
        #                 'ExternalImageId': 'string',
        #                 'Confidence': ...,
        #                 'IndexFacesModelVersion': 'string',
        #                 'UserId': 'string'
        #             }
        #         },
        #     ],
        #     'FaceModelVersion': 'string'
        # }
        result = []
        for face in faces['FaceMatches']:
            item = dynamodb_table.get_item(Key={'FaceId': face["Face"]["FaceId"]})
            if "Item" in item:
                result.append(item['Item']["object_metadata"])
        return {
            'statusCode': 200,
            'data': result
        }
    except rekognition_client.exceptions.InvalidS3ObjectException:
        print("ERROR: InvalidS3ObjectException")
        return {'statusCode': 406, 'data': None}
    except rekognition_client.exceptions.InvalidParameterException:
        # If no faces are detected in the input image, SearchFacesByImage returns an InvalidParameterException error
        return {'statusCode': 200, 'data': None}
    except rekognition_client.exceptions.ImageTooLargeException:
        print("ERROR: ImageTooLargeException")
        return {'statusCode': 406, 'data': None}
    except rekognition_client.exceptions.AccessDeniedException:
        print("ERROR: AccessDeniedException")
        return {'statusCode': 403, 'data': None}
    except rekognition_client.exceptions.InternalServerError:
        print("ERROR: InternalServerError")
        return {'statusCode': 500, 'data': None}
    except rekognition_client.exceptions.ThrottlingException:
        print("ERROR: ThrottlingException")
        return {'statusCode': 401, 'data': None}
    except rekognition_client.exceptions.ProvisionedThroughputExceededException:
        print("ERROR: ProvisionedThroughputExceededException")
        return {'statusCode': 401, 'data': None}
    except rekognition_client.exceptions.ResourceNotFoundException:
        print("ERROR: ResourceNotFoundException")
        return {'statusCode': 404, 'data': None}
    except rekognition_client.exceptions.InvalidImageFormatException:
        print("ERROR: InvalidImageFormatException")
        return {'statusCode': 406, 'data': None}
    except Exception:
        return {'statusCode': 500, 'data': None}
