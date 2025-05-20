import json
import os
import boto3
from botocore.exceptions import ClientError



def main(event, context):
    dynamodb = boto3.resource("dynamodb")
    S3_BUCKET = os.environ.get('S3_BUCKET')
    DYNAMO_TABLE = os.environ.get('DYNAMO_TABLE')
    table = dynamodb.Table(DYNAMO_TABLE)
    s3_client = boto3.client(
    's3',
    region_name='eu-central-1',
    endpoint_url='https://s3.eu-central-1.amazonaws.com'  
)
    try:
        # Validate required path parameter
        path_params = event.get("pathParameters")
        if not path_params or "task_id" not in path_params:
            return _response(400, {"error": "Missing 'task_id' in pathParameters."})
        task_id = path_params["task_id"]

        # Parse body
        try:
            body = json.loads(event.get("body", "{}"))
        except json.JSONDecodeError:
            return _response(400, {"error": "Request body is not valid JSON."})

        # Validate file_name
        file_name = body.get("file_name")
        if not file_name:
            return _response(400, {"error": "Missing 'file_name' in request body."})

        # Check if task exists in DynamoDB
        try:
            db_response = table.get_item(Key={'task_id': task_id})
        except ClientError as e:
            return _response(500, {"error": "DynamoDB error", "details": str(e)})

        if "Item" not in db_response:
            return _response(404, {"error": f"Task ID '{task_id}' not found."})

        # Generate S3 pre-signed URL
        try:
            object_key = f"{task_id}/{file_name}"
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': S3_BUCKET, 'Key': object_key},
                ExpiresIn=3600
            )
        except ClientError as e:
            return _response(500, {"error": "Failed to generate presigned URL", "details": str(e)})

        return _response(201, {"upload_url": presigned_url})

    except Exception as e:
        # Catch-all for unexpected errors
        return _response(500, {"error": "Unexpected error occurred", "details": str(e)})

def _response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
             "Content-Type": "application/json"
        }
    }
