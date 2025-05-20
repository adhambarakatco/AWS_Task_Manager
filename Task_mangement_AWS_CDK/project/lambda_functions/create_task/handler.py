import json
import uuid
import boto3
import os
import pg8000
import time
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMO_TABLE"])
db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']

def main(event, context):
    
    try:
        conn = pg8000.connect(
        host=db_host,        
        database=db_name, 
        user=db_user,   
        password=db_password
        )
        body = json.loads(event.get("body", "{}"))

        cur = conn.cursor()

    
        if "title" not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required field: title"})
            }
        
        user_id = event['requestContext']['authorizer']['claims']['sub']
        title=body["title"]
        desc=body["description"]
        prio=body["priority"]
        date=body["dueDate"]
        task_id = str(uuid.uuid4())

       
        item = {
            "task_id": task_id,
            "title": title,
            "description":desc,
            "priority":prio,
            "dueDate":date,
            "completed": False
        }

        table.put_item(Item=item)
        cur.execute("CREATE TABLE IF NOT EXISTS user_tasks (user_id UUID, task_id UUID, PRIMARY KEY (user_id, task_id));")
        cur.execute("INSERT INTO user_tasks (user_id, task_id) VALUES (%s, %s)", (user_id, task_id))
        conn.commit()
        cur.close()
        conn.close()

        
        return {
            "statusCode": 201,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
            "body": json.dumps(item)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
            "body": json.dumps({"error": str(e)})
        }
