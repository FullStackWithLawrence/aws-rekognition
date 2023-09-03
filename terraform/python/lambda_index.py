import os
import json
import boto3
from decimal import Decimal
from urllib.parse import unquote_plus
from rekognition_image import RekognitionCollection, RekognitionImage

rekognition = boto3.client('rekognition')
s3_resource = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

COLLECTION_ID = os.environ["COLLECTION_ID"]
TABLE_ID = os.environ["TABLE_ID"]
max_faces = int(os.environ["MAX_FACES_COUNT"])

collection = rekognition.describe_collection(CollectionId=COLLECTION_ID)
collection["CollectionId"] = COLLECTION_ID

rekognition_collection = RekognitionCollection(collection, rekognition)
table = dynamodb.Table(TABLE_ID)


def lambda_handler(event, context):
    if 'Records' in event:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            try:
                s3_object = s3_resource.Object(bucket, key)
                object_metadata = s3_object.metadata
                image = RekognitionImage.from_bucket(s3_object, rekognition)
                indexed_faces, _ = rekognition_collection.index_faces(image, max_faces)
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
