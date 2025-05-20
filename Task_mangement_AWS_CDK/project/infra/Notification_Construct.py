from constructs import Construct
from aws_cdk import (
    Duration,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_lambda_event_sources as lambda_event_sources
)

class NotificationL3Construct(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        # DLQ
        self.dlq = sqs.Queue(
            self, "NotificationDLQ",
            queue_name="notification-dlq",
            retention_period=Duration.days(14)
        )

        # Main SQS Queue
        self.queue = sqs.Queue(
            self, "NotificationQueue",
            queue_name="notification-queue",
            visibility_timeout=Duration.seconds(15),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self.dlq
            )
        )
        
        # PROPERTIES OF THE SQS QUEUE:
        # 1)SQS QUEUE URL:
        @property
        def queue_url(self):
            return self.queue.queue_url
        
        # 2)SQS QUEUE ARN:
        @property
        def queue_arn(self):
            return self.queue.queue_arn

        # Custom IAM Role for Lambda (with both AWS managed and inline policies)
        self.lambda_role = iam.Role(
            self, "NotificationLambdaRole",
            role_name="notification-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                # CloudWatch Logs permissions ('LambdaBasicExecutionRole')
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Attaching an inline policy to the lambda role:

        # 1) SQS permissions
        self.lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:GetQueueUrl",
                "sqs:ChangeMessageVisibility"
            ],
            resources=[self.queue.queue_arn]
        ))

        # 2) SES permissions
        self.lambda_role.add_to_policy(iam.PolicyStatement(
            actions=["ses:SendEmail"],
            resources=["*"]  
        ))


        # Lambda Function Definition
        self.notification_lambda = _lambda.Function(
            self, "NotificationLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            function_name="notification-lambda",
            description="Lambda function designed to send notification emails after a task is updated.",
            handler="handler.main", 
            code=_lambda.Code.from_asset("project/lambda_functions/notifications"),
            timeout=Duration.seconds(10),
            environment={
                "SENDER_EMAIL": "alii.amrr.hanyy@gmail.com"
            },
            role=self.lambda_role
        )

        # Add SQS event source to Lambda (Trigger)
        self.notification_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(self.queue)
        )