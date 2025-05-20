import json
import boto3
import os
import pg8000
import logging

# Initialize resources
s3 = boto3.client('s3')
dynamodb = boto3.resource("dynamodb")
S3_BUCKET = os.environ.get('S3_BUCKET')
table = dynamodb.Table(os.environ["DYNAMO_TABLE"])
db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(event, context):
    task_id = event["pathParameters"]["task_id"]

    try:
        # Connect to DB
        conn = pg8000.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cur = conn.cursor()

        # Delete from DynamoDB
        table.delete_item(Key={"task_id": task_id})
        logger.info(f"Deleted task {task_id} from DynamoDB")

        # Delete attachments from S3
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"{task_id}/")

        if 'Contents' in response and response['Contents']:
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            s3.delete_objects(
                Bucket=S3_BUCKET,
                Delete={'Objects': objects_to_delete}
            )
            logger.info(f"Deleted {len(objects_to_delete)} objects from S3 for task {task_id}")
        else:
            logger.info(f"No S3 objects to delete for task {task_id}")

        # Delete from user_tasks table
        cur.execute("DELETE FROM user_tasks WHERE task_id = %s", (task_id,))
        logger.info(f"Deleted task {task_id} from RDS")

        # Commit and clean up
        conn.commit()
        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Task {task_id} deleted"}),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                "Content-Type": "application/json"
            }
        }

    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to delete task {task_id}"}),
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
                "Content-Type": "application/json"
            }
        }
