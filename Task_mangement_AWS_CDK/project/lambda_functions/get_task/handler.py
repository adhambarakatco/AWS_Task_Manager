import json
import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMO_TABLE"])

s3_bucket = os.environ['S3_BUCKET']
s3_client = boto3.client('s3')

def main(event, context):
    try:
        task_id = event["pathParameters"]["task_id"]

        try:
            response = table.get_item(Key={"task_id": task_id})
        except ClientError as e:
            return {
                "statusCode": 502,
                "body": json.dumps({"message": "Error accessing database", "error": e.response['Error']['Message']})
            }

        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": f"Task with id '{task_id}' not found"}),
            }

        prefix = f"{task_id}/"
        files = []

        try:
            s3_response = s3_client.list_objects_v2(
                Bucket=s3_bucket,
                Prefix=prefix  
            )
        except ClientError as e:
            return {
                "statusCode": 502,
                "body": json.dumps({"message": "Error accessing S3 bucket", "error": e.response['Error']['Message']})
            }
        
        if 'Contents' in s3_response:
            files = [obj['Key'] for obj in s3_response['Contents']]

        return {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "task": item,  
                "attachments": files  
            })
        }

    except KeyError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Missing path parameter: {str(e)}"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error", "error": str(e)})
        }
