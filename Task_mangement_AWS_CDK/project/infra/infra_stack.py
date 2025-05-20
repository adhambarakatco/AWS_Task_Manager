from aws_cdk import (
    Duration,
    Stack,
    NestedStack,
    RemovalPolicy
)

import os
import time
from aws_cdk import aws_ec2 as ec2, aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from .EC2_construct import EC2InstanceConstruct
from .RDS_construct import RDSInstanceConstruct
from .IAM_construct import IAMConstruct
from .Cognito_construct import CognitoConstruct
from .Lambda_APIGateway_construct import LambdaApiGatewayConstruct
from .CloudWatch_construct import CloudWatchConstruct
from .Notification_Construct import NotificationL3Construct


class infra_stack(NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(self, "MyVPC",
                           max_azs=2,
                           nat_gateways=0,
                           subnet_configuration=[
                               ec2.SubnetConfiguration(
                                   name="Public",
                                   subnet_type=ec2.SubnetType.PUBLIC,
                                   cidr_mask=24
                               ),
                               ec2.SubnetConfiguration(
                                   name="Private",
                                   subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                                   cidr_mask=24
                               )
                           ]
                           )

        # Create S3 bucket for file attachments
        self.s3 = s3.Bucket(self, "Task_Management_Attachments",
                            removal_policy=RemovalPolicy.DESTROY,  # For dev/testing — delete bucket on stack destroy
                            auto_delete_objects=True,
                            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                            encryption=s3.BucketEncryption.S3_MANAGED)

        # Create DynamoDB table for task metadata with Global Secondary Index for user_id
        self.dynamo_db = dynamodb.TableV2(self, "Task_Metadata",
                                          partition_key=dynamodb.Attribute(
                                              name="task_id",
                                              type=dynamodb.AttributeType.STRING
                                          ),
                                          table_name="task_metadata",
                                          billing=dynamodb.Billing.on_demand(),
                                          removal_policy=RemovalPolicy.DESTROY
                                          )


        # Add VPC Endpoints for S3, DynamoDB and SQS 
        self.vpc.add_gateway_endpoint("S3_Endpoint",
                                      service=ec2.GatewayVpcEndpointAwsService.S3)

        self.vpc.add_gateway_endpoint("DynamoDB_Endpoint",
                                      service=ec2.GatewayVpcEndpointAwsService.DYNAMODB)
        
        self.vpc.add_interface_endpoint("SQS_Endpoint",
                                        service=ec2.InterfaceVpcEndpointAwsService.SQS)

        # Create IAM roles and policies
        self.iam = IAMConstruct(self, "IAM",
                                s3_bucket=self.s3,
                                dynamodb_table=self.dynamo_db)

        # Create EC2 instance with the proper IAM role
        self.ec2 = EC2InstanceConstruct(self, "EC2",
                                        vpc=self.vpc,
                                        ec2_role=self.iam.ec2_role)

        # Create RDS instance
        self.rds = RDSInstanceConstruct(self, "RDS",
                                        vpc=self.vpc,
                                        db_name="TaskManagement",
                                        db_username='adminusr',
                                        db_password='adminpwrd'
                                        )

        # Grant EC2 access to RDS
        self.rds.security_group.add_ingress_rule(
            ec2.Peer.security_group_id(self.ec2.security_group.security_group_id),
            ec2.Port.tcp(5432),
            "Allow EC2 access to RDS"
        )

        # Create Cognito User Pool for authentication
        self.cognito = CognitoConstruct(self, "Cognito")

        
        DB_CREDS={"DB_HOST":self.rds.DB_HOST,
                  "DB_NAME":self.rds.DB_NAME,
                  "DB_USER":self.rds.DB_USER,
                  "DB_PASS":self.rds.DB_PASS}
        
        # NOTIFICATIONS CONSTRUCT 
        # Create Notification Construct (Contains all the notification related resources and permissions)
        self.notification_construct = NotificationL3Construct(
            self, "NotificationConstruct"
        )

        # Create Lambda functions and API Gateway
        self.lambda_api = LambdaApiGatewayConstruct(self, "LambdaAPI",
                                                    cognito_user_pool=self.cognito.user_pool,
                                                    dynamo_table=self.dynamo_db,
                                                    s3_bucket=self.s3,
                                                    notification_queue=self.notification_construct.queue,
                                                    lambda_role=self.iam.lambda_role,
                                                    DB_CREDS=DB_CREDS,
                                                    vpc=self.vpc
                                                    )
        
        # GRANT SEND PERMISSIONS TO THE update_task_lambda (FOR NOTIFICATION SQS QUEUE)
        self.notification_construct.queue.grant_send_messages(self.lambda_api.update_task_lambda)

        # Set up CloudWatch monitoring 
        lambda_functions = [
            self.lambda_api.get_tasks_lambda,
            self.lambda_api.get_task_lambda,
            self.lambda_api.create_task_lambda,
            self.lambda_api.update_task_lambda,
            self.lambda_api.delete_task_lambda,
            self.lambda_api.upload_attachment_lambda,
            self.notification_construct.notification_lambda
        ]

        self.cloudwatch = CloudWatchConstruct(self, "CloudWatch",
                                              api=self.lambda_api.api,
                                              lambda_functions=lambda_functions,
                                              dynamodb_table=self.dynamo_db,
                                            #   s3_bucket=self.s3,
                                              sqs_queue=self.notification_construct.queue,)
        
       