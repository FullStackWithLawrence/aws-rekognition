import os
import json
import boto3
from decimal import Decimal
from urllib.parse import unquote_plus
import logging

COLLECTION_ID = os.environ["COLLECTION_ID"]
TABLE_ID = os.environ["TABLE_ID"]
MAX_FACES = int(os.environ["MAX_FACES_COUNT"])
DEBUG_MODE = False or bool(os.environ["DEBUG_MODE"])


s3_client = boto3.resource('s3')

dynamodb_client = boto3.resource('dynamodb')
dynamodb_table = dynamodb_client.Table(TABLE_ID)

rekognition_client = boto3.client('rekognition')
rekognition_collection = rekognition_client.describe_collection(CollectionId=COLLECTION_ID)

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

def lambda_handler(event, context):
    if 'Records' in event:
        s3_bucket_name = event['Records'][0]['s3']['bucket']['name']
        for record in event['Records']:
            key = unquote_plus(record['s3']['object']['key'], encoding='utf-8')
            try:
                s3_object = s3_client.Object(s3_bucket_name, key)
                object_metadata = {key.replace("x-amz-meta-", ""): s3_object.metadata[key] for key in s3_object.metadata.keys()}

                if DEBUG_MODE:
                    print("record: {var}".format(var=json.dumps(record, indent = 4)))
                    print("key={key}, s3_object={s3_object}, object_metadata={object_metadata}".format(
                        s3_object=s3_object,
                        key=key,
                        object_metadata=object_metadata
                        ))

                # analyze our newly uploaded image.
                # index_faces() will return a dict of 'faceprint' dicts
                # see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition/client/index_faces.html#
                indexed_faces = rekognition_client.index_faces(
                    CollectionId=COLLECTION_ID,
                    Image={
                        'S3Object': {
                                    'Bucket': s3_bucket_name,
                                    'Name': key
                                    }
                           },
                    ExternalImageId=key,
                    MaxFaces=MAX_FACES,
                    QualityFilter="AUTO",
                    DetectionAttributes=['ALL']
                    )

                # persist all of the 'faceprints' to our DynamoDB table
                if type(indexed_faces) == dict:
                    for indexed_face in indexed_faces:
                        if not hasattr(indexed_face, "to_dict"):
                            print("WARNING: indexed_face is not a serializable Dict object: {v}".format(
                                v=indexed_face
                            ))
                            return ''
                        face = indexed_face.to_dict()
                        face["FaceId"] = face['face_id']
                        face["bucket"] = s3_bucket_name
                        face["key"] = key
                        face["object_metadata"] = {key.replace("x-amz-meta-", ""): object_metadata[key] for key in object_metadata.keys()}
                        del face['face_id']
                        face = json.loads(json.dumps(face), parse_float=Decimal)
                        dynamodb_table.put_item(Item=face)
                else:
                    print("WARNING: expected a Dict object from rekognition_client.index_faces() but received {t}".format(
                        t=type(indexed_faces)
                    ))
                    if type(indexed_faces) == str:
                        print(indexed_faces)
                return ''
            except Exception as e:
                print(e)
                print("Error processing object {} from bucket {}. ".format(key, s3_bucket_name) +
                      "Make sure your object and bucket exist and your bucket is in the same region as this function.")
                raise e
    return ''
