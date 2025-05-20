import json
import boto3
import os

ses = boto3.client('ses')

def main(event, context):
    print("Lambda triggered. Event:", json.dumps(event))  

    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            print("Parsed body:", body)  
            
            # Extracting the data (Email, task name, and completion status)
            email = body['email']
            task_name = body['task_name']
            completion_str = "Complete" if body.get("completed") else "In Progress"

            # The Email message
            message = (
                    "Your task was updated successfully.\n\n"
                    "Current task details:\n"
                    f"Title: {task_name}\n"
                    f"Completion status: {completion_str}"
            )

            response = ses.send_email(
                Source=os.environ['SENDER_EMAIL'],
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': 'Your Task Has Been Updated'},
                    'Body': {'Text': {'Data': message}}
                }
            )
            print("Email sent to:", email, "Response:", response)

        except Exception as e:
            print("Failed to process record or send email:", e)