from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_sqs as sqs,
    Duration,
    CfnOutput
)
from constructs import Construct


class CloudWatchConstruct(Construct):
    def __init__(
            self,
            scope: Construct,
            id: str,
            *,
            api=None,
            lambda_functions=None,
            dynamodb_table=None,
            s3_bucket=None,
            sqs_queue=None,
            **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        # Create a CloudWatch dashboard
        self.dashboard = cloudwatch.Dashboard(
            self, "TaskManagerDashboard",
            dashboard_name="TaskManagerDashboard"
        )

        # Add DynamoDB metrics if table is provided
        if dynamodb_table:
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title="DynamoDB Read/Write Capacity",
                    left=[
                        dynamodb_table.metric_consumed_read_capacity_units(
                            statistic="sum",
                            period=Duration.minutes(5)
                        ),
                        dynamodb_table.metric_consumed_write_capacity_units(
                            statistic="sum",
                            period=Duration.minutes(5)
                        )
                    ]
                )
            )

            # Add DynamoDB Throttled Events widget
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title="DynamoDB Throttled Events",
                    left=[
                        dynamodb_table.metric("ReadThrottleEvents",
                                              statistic="sum",
                                              period=Duration.minutes(5)
                                              ),
                        dynamodb_table.metric("WriteThrottleEvents",
                                              statistic="sum",
                                              period=Duration.minutes(5)
                                              )
                    ]
                )
            )

       # Add S3 bucket metrics dynamically
        if s3_bucket:
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title="S3 Bucket Size",
                    left=[
                        s3_bucket.metric("BucketSizeBytes",
                                        statistic="sum",
                                        period=Duration.days(1),
                                        unit=cloudwatch.Unit.BYTES)
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="S3 Number of Objects",
                    left=[
                        s3_bucket.metric("NumberOfObjects",
                                        statistic="sum",
                                        period=Duration.days(1),
                                        unit=cloudwatch.Unit.COUNT)
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="S3 Requests",
                    left=[
                        s3_bucket.metric("AllRequests",
                                        statistic="sum",
                                        period=Duration.minutes(5)),
                        s3_bucket.metric("GetRequests",
                                        statistic="sum",
                                        period=Duration.minutes(5)),
                        s3_bucket.metric("PutRequests",
                                        statistic="sum",
                                        period=Duration.minutes(5))
                    ]
                )
            )

            # Create S3 error rate alarm dynamically (based on 4xxErrors)
            self.s3_error_alarm = cloudwatch.Alarm(
                self, "S3ErrorRateAlarm",
                metric=s3_bucket.metric("4xxErrors"),
                threshold=10,
                evaluation_periods=1,
                alarm_description="Alarm if S3 bucket has too many 4XX errors",
                alarm_name="S3ClientErrorRate"
            )


        # Add SQS queue metrics if provided
        if sqs_queue:
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title="SQS Messages",
                    left=[
                        sqs_queue.metric("NumberOfMessagesSent",
                                         statistic="sum",
                                         period=Duration.minutes(5)
                                         ),
                        sqs_queue.metric("NumberOfMessagesReceived",
                                         statistic="sum",
                                         period=Duration.minutes(5)
                                         ),
                        sqs_queue.metric("ApproximateNumberOfMessagesVisible",
                                         statistic="avg",
                                         period=Duration.minutes(5)
                                         )
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="SQS Queue Age",
                    left=[
                        sqs_queue.metric("ApproximateAgeOfOldestMessage",
                                         statistic="maximum",
                                         period=Duration.minutes(5),
                                         unit=cloudwatch.Unit.SECONDS
                                         )
                    ]
                )
            )

            # Create SQS alarms for queue depth
            self.sqs_queue_depth_alarm = cloudwatch.Alarm(
                self, "SQSQueueDepthAlarm",
                metric=sqs_queue.metric("ApproximateNumberOfMessagesVisible"),
                threshold=100,
                evaluation_periods=3,
                alarm_description="Alarm if the SQS queue has too many messages",
                alarm_name="SQSQueueDepth"
            )

            # Create alarm for SQS oldest message age (potential processing issue)
            self.sqs_age_alarm = cloudwatch.Alarm(
                self, "SQSMessageAgeAlarm",
                metric=sqs_queue.metric("ApproximateAgeOfOldestMessage"),
                threshold=900,  # 15 minutes
                evaluation_periods=3,
                alarm_description="Alarm if messages are not being processed",
                alarm_name="SQSMessageAge"
            )

        # Add Lambda metrics if functions are provided
        if lambda_functions:
            # Create metrics for each Lambda function
            lambda_metrics = []
            error_metrics = []
            duration_metrics = []

            for lambda_func in lambda_functions:
                if isinstance(lambda_func, lambda_.Function):
                    lambda_metrics.append(
                        lambda_func.metric_invocations(
                            statistic="sum",
                            period=Duration.minutes(5)
                        )
                    )

                    error_metrics.append(
                        lambda_func.metric_errors(
                            statistic="sum",
                            period=Duration.minutes(5)
                        )
                    )

                    duration_metrics.append(
                        lambda_func.metric_duration(
                            statistic="avg",
                            period=Duration.minutes(5)
                        )
                    )

            # Add Lambda invocations widget
            if lambda_metrics:
                self.dashboard.add_widgets(
                    cloudwatch.GraphWidget(
                        title="Lambda Function Invocations",
                        left=lambda_metrics
                    )
                )

            # Add Lambda errors widget
            if error_metrics:
                self.dashboard.add_widgets(
                    cloudwatch.GraphWidget(
                        title="Lambda Function Errors",
                        left=error_metrics
                    )
                )

            # Add Lambda duration widget
            if duration_metrics:
                self.dashboard.add_widgets(
                    cloudwatch.GraphWidget(
                        title="Lambda Function Duration",
                        left=duration_metrics
                    )
                )

        # Add API Gateway metrics if API is provided
        if api:
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title="API Gateway Requests",
                    left=[
                        api.metric_count(
                            statistic="sum",
                            period=Duration.minutes(5)
                        )
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="API Gateway Latency",
                    left=[
                        api.metric_latency(
                            statistic="avg",
                            period=Duration.minutes(5)
                        )
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="API Gateway 4XXError",
                    left=[
                        api.metric_client_error(
                            statistic="sum",
                            period=Duration.minutes(5)
                        )
                    ]
                ),
                cloudwatch.GraphWidget(
                    title="API Gateway 5XXError",
                    left=[
                        api.metric_server_error(
                            statistic="sum",
                            period=Duration.minutes(5)
                        )
                    ]
                )
            )

        # Create CloudWatch alarms for high error rates
        if api:
            self.api_error_alarm = cloudwatch.Alarm(
                self, "ApiErrorRateAlarm",
                metric=api.metric_server_error(),
                threshold=5,
                evaluation_periods=1,
                alarm_description="Alarm if the API has too many 5XX errors",
                alarm_name="ApiServerErrorRate"
            )

        # Output Dashboard URL
        CfnOutput(
            self, "DashboardURL",
            value=f"https://console.aws.amazon.com/cloudwatch/home#dashboards:name={self.dashboard.dashboard_name}",
            description="URL for the CloudWatch Dashboard"
        )
