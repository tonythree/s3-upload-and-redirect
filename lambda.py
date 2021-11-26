import logging
import boto3
from botocore.exceptions import ClientError
import os
s3_client = boto3.client('s3')
BUCKET = "bucket-name"
folder = './tmp/'
filename = 'test.xlsx'

def upload_file(bucket_name, file_name,  object_name=None):
    """Upload a file to an S3 bucket

    :param bucket_name: Bucket to upload to
    :param file_name: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def handler(event, context):
    # store a file in s3
    stored = upload_file(BUCKET, folder+filename)
    # generate a presigned url to the file
    url = generate_presigned_url(BUCKET, filename)
    
    if stored and url:
        # return the url as a redirect
        return {
            'statusCode': 301,
            'headers': {
                'Location': url
            }
        }
    else:
        return {
            'statusCode': 500,
            'body': 'Error storing file in s3'
        }

print(handler(None, None))
