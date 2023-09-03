# see https://docs.aws.amazon.com/rekognition/latest/dg/example_rekognition_Usage_FindFacesInCollection_section.html

import os
import uuid
import boto3
import base64
from rekognition_image_detection import RekognitionCollection, RekognitionImage

rekognition = boto3.client('rekognition')
s3_resource = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

max_faces = int(os.environ["MAX_FACES_COUNT"])
threshold = float(os.environ["FACE_DETECT_THRESHOLD"])

COLLECTION_ID = os.environ["COLLECTION_ID"]
TABLE_ID = os.environ["TABLE_ID"]

collection = rekognition.describe_collection(CollectionId=COLLECTION_ID)
collection["CollectionId"] = COLLECTION_ID
rekognition_collection = RekognitionCollection(collection, rekognition)

table = dynamodb.Table(TABLE_ID)


def lambda_handler(event, context):
    try:
        image = event['image']
        image = base64.b64decode(image.encode())
        data = {'Bytes': image}

        image = RekognitionImage(data, image_name=str(uuid.uuid4()), rekognition_client=rekognition)
        _, collection_faces = rekognition_collection.search_faces_by_image(image, threshold, max_faces)
        result = []
        for collection_face in collection_faces:
            item = table.get_item(Key={'FaceId': collection_face.face_id})
            if "Item" in item:
                result.append(item['Item']["object_metadata"])
        return {
            'statusCode': 200,
            'data': result
        }
    except Exception as e:
        print(e)
        print("Error processing object", event)
        raise e
