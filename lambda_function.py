from __future__ import print_function
import boto3
from decimal import Decimal
import json
import urllib

print('Loading function')

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')


# --------------- Helper Functions ------------------

def index_faces(bucket, key):
    response = rekognition.index_faces(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key
            }
        },
        CollectionId="studentsimg"
    )
    return response

def update_index(tableName, faceId, fullName, email):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'RekognitionId': {'S': faceId},
            'FullName': {'S': fullName},
            'Email': {'S': email}
        }
    ) 

# --------------- Main handler ------------------

def lambda_handler(event, context):

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    print("Records: ", event['Records'])
    key = event['Records'][0]['s3']['object']['key']
    print("Key: ", key)

    try:

        # Calls Amazon Rekognition IndexFaces API to detect faces in S3 object 
        # to index faces into the specified collection
        response = index_faces(bucket, key)
        
        # Commit faceId, full name, and email to DynamoDB
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']

            ret = s3.head_object(Bucket=bucket, Key=key)
            personFullName = ret['Metadata'].get('fullname', '')  # Get the full name from object metadata
            personEmail = ret['Metadata'].get('email', '')  # Get the email from object metadata

            update_index('students_data', faceId, personFullName, personEmail)

        # Print response to console
        print(response)

        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise e