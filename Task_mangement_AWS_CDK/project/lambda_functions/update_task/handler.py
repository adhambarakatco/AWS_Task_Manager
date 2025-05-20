import json
import boto3
import os
import logging

'''
This Lambda function does the following:

1) It updates a task in DynamoDB based on the task ID provided in the path parameters.
2) It sends a notification to the notification SQS queue with the task name and the user's email. (To be processed later for SES)

'''

# Initializing the clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMO_TABLE"])
sqs = boto3.client("sqs")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(event, context):
    try:
        # UPDATING THE TASK IN DYNAMODB

        # Extracting task ID
        task_id = event["pathParameters"].get("task_id")
        if not task_id:
            return {
                "statusCode": 400,
                'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
                "body": json.dumps({"error": "Missing task ID in path parameters"})
            }

        # Parsing the body (To check if the title is present)
        body = json.loads(event.get("body", "{}"))
        if "title" not in body:
            return {
                "statusCode": 400,
                'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
                "body": json.dumps({"error": "Missing required field: title"})
            }

        new_title = body["title"]
        is_completed = body.get("completed", False)

        # Update task in DynamoDB
        response = table.update_item(
            Key={"task_id": task_id},
            UpdateExpression="SET title = :title, completed = :completed , dueDate=:dueDate , priority=:priority , description=:description",
            ExpressionAttributeValues={
                ":title": body["title"],
                ":completed": body["completed"],
                ":dueDate":body["dueDate"],
                ":priority":body["priority"],
                ":description":body["description"]
            },
            ReturnValues="ALL_NEW"
        )
        
        # SENDING THE NOTIFICATION TO SQS (EMAIL AND TASK NAME)

        # Get email from Cognito claims
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        email = claims.get("email")

        if not email:
            logger.warning("Email not found in Cognito claims")
        else:
            # Send the notification message to SQS
            sqs.send_message(
                QueueUrl=os.environ["SQS_QUEUE_URL"],
                MessageBody=json.dumps({
                    "task_name": new_title,
                    "email": email,
                    "completed": is_completed
                })
            )
            logger.info(f"Notification enqueued for {email} and task '{new_title}'")

        return {
            "statusCode": 200,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
            "body": json.dumps(response["Attributes"])
        }

    except Exception as e:
        logger.error("Error occurred while updating task or sending notification", exc_info=True)
        return {
            "statusCode": 500,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
            "body": json.dumps({"error": str(e)})
        }
