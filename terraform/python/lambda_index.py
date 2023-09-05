import os
import json
import boto3
from decimal import Decimal
from urllib.parse import unquote_plus

COLLECTION_ID = os.environ["COLLECTION_ID"]
TABLE_ID = os.environ["TABLE_ID"]
MAX_FACES = int(os.environ["MAX_FACES_COUNT"])

rekognition_client = boto3.client('rekognition')
s3_client = boto3.resource('s3')
dynamodb_client = boto3.resource('dynamodb')
collection = rekognition_client.describe_collection(CollectionId=COLLECTION_ID)
table = dynamodb_client.Table(TABLE_ID)

def lambda_handler(event, context):
    if 'Records' in event:
        bucket = event['Records'][0]['s3']['bucket']['name']
        for record in event['Records']:
            print("record: {var}".format(var=json.dumps(record, indent = 4)))
            key = unquote_plus(record['s3']['object']['key'], encoding='utf-8')
            try:
                s3_object = s3_client.Object(bucket, key)
                object_metadata = {key.replace("x-amz-meta-", ""): s3_object.metadata[key] for key in s3_object.metadata.keys()}
                print("key={key}, s3_object={s3_object}, object_metadata={object_metadata}".format(
                    s3_object=s3_object,
                    key=key,
                    object_metadata=object_metadata
                    ))
                # see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition/client/index_faces.html#
                indexed_faces = rekognition_client.index_faces(
                    CollectionId=COLLECTION_ID,
                    Image={
                        'S3Object': {
                                    'Bucket': bucket,
                                    'Name': key
                                    }
                           },
                    ExternalImageId=key,
                    MaxFaces=MAX_FACES,
                    QualityFilter="AUTO",
                    DetectionAttributes=['ALL']
                    )

                for indexed_face in indexed_faces:
                    face = indexed_face.to_dict()
                    face["FaceId"] = face['face_id']
                    face["bucket"] = bucket
                    face["key"] = key
                    face["object_metadata"] = {key.replace("x-amz-meta-", ""): object_metadata[key] for key in object_metadata.keys()}
                    del face['face_id']
                    face = json.loads(json.dumps(face), parse_float=Decimal)
                    table.put_item(Item=face)
                return ''
            except Exception as e:
                print(e)
                print("Error processing object {} from bucket {}. ".format(key, bucket) +
                      "Make sure your object and bucket exist and your bucket is in the same region as this function.")
                raise e
    return ''
