from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_cognito as cognito,
    aws_ec2 as ec2,
    aws_sqs as sqs,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct
import os


class LambdaApiGatewayConstruct(Construct):
    def __init__(
            self,
            scope: Construct,
            id: str,
            *,
            vpc,
            cognito_user_pool=None,
            dynamo_table=None,
            s3_bucket=None,
            notification_queue=None,
            lambda_role=None,
            DB_CREDS=None,
            **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        # Common environment variables for Lambda functions
        lambda_env = {
            "DYNAMO_TABLE": dynamo_table.table_name if dynamo_table else "",
            "S3_BUCKET": s3_bucket.bucket_name if s3_bucket else "",
            "SQS_QUEUE_URL": notification_queue.queue_url if notification_queue else "",
            "DB_HOST": DB_CREDS['DB_HOST'],
            "DB_NAME": DB_CREDS['DB_NAME'],
            "DB_USER":DB_CREDS['DB_USER'],
            "DB_PASSWORD":DB_CREDS['DB_PASS']
        }



        lambda_layer = lambda_.LayerVersion(
        self, 'LambdaLayer',
        code=lambda_.Code.from_asset('project/lambda_functions/lambda_layer/my-lambda-layer.zip'),
        compatible_runtimes=[lambda_.Runtime.PYTHON_3_10],
        description="PostgreSQL dependencies layer")


        # Create Lambda functions for task operations
        self.get_tasks_lambda = lambda_.Function(
            self, "GetAllTasksFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="handler.main",
            code=lambda_.Code.from_asset("project/lambda_functions/get_all_tasks"),
            timeout=Duration.seconds(30),
            environment=lambda_env,
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_WEEK,
            layers=[lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        self.get_task_lambda = lambda_.Function(
            self, "GetTaskFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="handler.main",
            code=lambda_.Code.from_asset("project/lambda_functions/get_task"),
            timeout=Duration.seconds(30),
            environment=lambda_env,
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_WEEK,
            layers=[lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        self.create_task_lambda = lambda_.Function(
            self, "CreateTaskFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="handler.main",
            code=lambda_.Code.from_asset("project/lambda_functions/create_task"),
            timeout=Duration.seconds(30),
            environment=lambda_env,
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_WEEK,
            layers=[lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        self.update_task_lambda = lambda_.Function(
            self, "UpdateTaskFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="handler.main",
            code=lambda_.Code.from_asset("project/lambda_functions/update_task"),
            timeout=Duration.seconds(30),
            environment=lambda_env,
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_WEEK,
            layers=[lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        self.delete_task_lambda = lambda_.Function(
            self, "DeleteTaskFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="handler.main",
            code=lambda_.Code.from_asset("project/lambda_functions/delete_task"),
            timeout=Duration.seconds(30),
            environment=lambda_env,
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_WEEK,
            layers=[lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        self.upload_attachment_lambda = lambda_.Function(
            self, "UploadAttachmentFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="handler.main",
            code=lambda_.Code.from_asset("project/lambda_functions/upload_file"),
            timeout=Duration.seconds(30),
            environment=lambda_env,
            role=lambda_role,
            log_retention=logs.RetentionDays.ONE_WEEK,
            layers=[lambda_layer],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        self.api = apigateway.RestApi(
            self, "TaskManagerApi",
            rest_api_name="Task Manager API",
            description="API for Task Management System",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,        # Allow all origins, change to specific if you want
                allow_methods=apigateway.Cors.ALL_METHODS,        # Allow all HTTP methods (GET, POST, etc)
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                    "X-Amz-User-Agent"
                ],
                allow_credentials=True   # Optional: allow cookies, authorization headers
            )
        )

        # Add Cognito authorizer if user pool provided
        authorizer = None
        if cognito_user_pool:
            authorizer = apigateway.CognitoUserPoolsAuthorizer(
                self, "TasksAuthorizer",
                cognito_user_pools=[cognito_user_pool]
            )

        # Define auth_type based on whether authorizer exists
        auth_type = apigateway.AuthorizationType.COGNITO if authorizer else apigateway.AuthorizationType.NONE

        # Add routes to API Gateway
        # Tasks resource
        tasks = self.api.root.add_resource("tasks")

        # GET /tasks
        tasks.add_method(
            "GET",
            apigateway.LambdaIntegration(self.get_tasks_lambda),
            authorizer=authorizer,
            authorization_type=auth_type
        )

        # POST /tasks
        tasks.add_method(
            "POST",
            apigateway.LambdaIntegration(self.create_task_lambda),
            authorizer=authorizer,
            authorization_type=auth_type
        )

        # Single task resource
        task = tasks.add_resource("{task_id}")

        # GET /tasks/{task_Id}
        task.add_method(
            "GET",
            apigateway.LambdaIntegration(self.get_task_lambda),
            authorizer=authorizer,
            authorization_type=auth_type
        )

        # PUT /tasks/{task_Id}
        task.add_method(
            "PUT",
            apigateway.LambdaIntegration(self.update_task_lambda),
            authorizer=authorizer,
            authorization_type=auth_type
        )

        # DELETE /tasks/{task_Id}
        task.add_method(
            "DELETE",
            apigateway.LambdaIntegration(self.delete_task_lambda),
            authorizer=authorizer,
            authorization_type=auth_type
        )

        # Attachment resource
        attachments = task.add_resource("attachments")

        # POST /tasks/{task_Id}/attachments
        attachments.add_method(
            "POST",
            apigateway.LambdaIntegration(self.upload_attachment_lambda),
            authorizer=authorizer,
            authorization_type=auth_type
        )

        # Output the API URL
        CfnOutput(
            self, "ApiUrl",
            value=self.api.url,
            description="URL of the Task Manager API"
        )