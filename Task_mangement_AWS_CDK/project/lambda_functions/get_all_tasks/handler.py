import json
import boto3
import os
import pg8000
import traceback
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS resources
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMO_TABLE"])
table_name = os.environ["DYNAMO_TABLE"]

# Get database connection parameters from environment variables
db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']

def get_user_id(event):
    """Extract user ID from event with proper error handling"""
    try:
        return event['requestContext']['authorizer']['claims']['sub']
    except KeyError as e:
        logger.error(f"Failed to extract user ID: {e}")
        # Log available keys for debugging
        if 'requestContext' in event:
            logger.info(f"requestContext keys: {list(event['requestContext'].keys())}")
            if 'authorizer' in event['requestContext']:
                logger.info(f"authorizer keys: {list(event['requestContext']['authorizer'].keys())}")
        raise ValueError(f"Authentication issue: {str(e)}")

def get_db_connection():
    """Create and return database connection with error handling"""
    try:
        return pg8000.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise ConnectionError(f"Failed to connect to database: {str(e)}")

def fetch_task_ids(conn, user_id):
    """Fetch task IDs from database for the given user"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT task_id FROM user_tasks WHERE user_id=%s", (user_id,))
        rows = cur.fetchall() or []
        cur.close()
        if not rows:
            logger.info("No tasks found for user")
            return []
        return [str(row[0]) for row in rows]
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        raise RuntimeError(f"Error retrieving task IDs: {str(e)}")

def fetch_tasks_from_dynamodb(task_ids):
    """Fetch task details from DynamoDB"""
    if not task_ids:
        return []
    
    try:
        response = dynamodb.batch_get_item(
            RequestItems={
                table_name: {
                    'Keys': [{'task_id': task_id} for task_id in task_ids]
                }
            }
        )
        return response['Responses'][table_name]
    except Exception as e:
        logger.error(f"DynamoDB error: {str(e)}")
        raise RuntimeError(f"Error retrieving tasks from DynamoDB: {str(e)}")

def main(event, context):
    """Main Lambda handler function with improved error handling"""
    conn = None
    try:
        # Get database connection
        conn = get_db_connection()
        
        # Get user ID from request context
        user_id = get_user_id(event)
        
        # Fetch task IDs for the user
        task_ids = fetch_task_ids(conn, user_id)
        if not task_ids:
             return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"  
            },
            "body": json.dumps({
                "count": 0
            })
        }



        
        # Fetch task details from DynamoDB
        items = fetch_tasks_from_dynamodb(task_ids)
        
        # Return successful response
        return {
            "statusCode": 200,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
            "body": json.dumps({
                "tasks": items,
                "count": len(items)
            })
        }
    
    except ValueError as e:
        # Authentication/authorization errors
        logger.error(f"Authorization error: {str(e)}")
        return {
            "statusCode": 401,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
            "body": json.dumps({"error": "Unauthorized. Valid authentication required."})
        }
    
    except ConnectionError as e:
        # Database connection errors
        logger.error(f"Database connection error: {str(e)}")
        return {
            "statusCode": 503,
           'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
            "body": json.dumps({"error": "Service temporarily unavailable. Please try again later."})
        }
    
    except Exception as e:
        # All other errors
        error_message = str(e)
        logger.error(f"Unexpected error: {error_message}")
        logger.error(traceback.format_exc())
        return {
            "statusCode": 500,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
            "body": json.dumps({"error": "An unexpected error occurred"})
        }
    
    finally:
        if conn:
            try:
                conn.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")