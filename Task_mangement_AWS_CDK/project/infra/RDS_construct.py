from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    aws_rds as rds,
    SecretValue,
    aws_secretsmanager as secretsmanager,
    CfnOutput
)
from constructs import Construct


class RDSInstanceConstruct(Construct):
    def __init__(
            self,
            scope: Construct,
            id: str,
            *,
            vpc: ec2.Vpc,
            db_name: str,
            db_username: str,
            db_password: str,
            **kwargs
    ):
        super().__init__(scope, id, **kwargs)



        # Create a Secrets Manager secret for database credentials
        # self.db_credentials = secretsmanager.Secret(
        #     self, "DBCredentials",
        #     description="Credentials for Task Management RDS instance",
        #     secret_name=f"task-management-db-credentials",
        #     generate_secret_string=secretsmanager.SecretStringGenerator(
        #         secret_string_template=f'{{"username": "{db_username}"}}',
        #         generate_string_key="password",
        #         exclude_characters="\"@/\\"
        #     )
        # )

        self.security_group = ec2.SecurityGroup(
            self, f"{id}RDS_SG",
            vpc=vpc,
            description=f"Security group for RDS {id}",
            allow_all_outbound=True
        )

        # Only allow access from resources within the VPC
        self.security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(5432),
            "Allow Postgres access from within VPC"
        )

        # Create the RDS instance using PostgreSQL
        self.rds_instance = rds.DatabaseInstance(
            self, id,
            vpc=vpc,
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_14  # RDS Version
            ),
            instance_type=ec2.InstanceType("t3.micro"),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            database_name=db_name,
            credentials=rds.Credentials.from_password(
                username=db_username,  
                password=SecretValue.unsafe_plain_text(db_password)  # Your hardcoded password
            ),
            multi_az=False,
            allocated_storage=20,
            security_groups=[self.security_group],
            removal_policy=RemovalPolicy.DESTROY,
            publicly_accessible=False,
            deletion_protection=False,  # Set to True for production
            backup_retention=Duration.days(7)
        )

        # Output database connection information
        CfnOutput(
            self, "DBEndpoint",
            value=self.rds_instance.db_instance_endpoint_address,
            description="Database endpoint address"
        )

        # CfnOutput(
        #     self, "DBSecretArn",
        #     value=self.db_credentials.secret_arn,
        #     description="Database credentials secret ARN"
        # )

        self.DB_HOST=self.rds_instance.db_instance_endpoint_address
        self.DB_USER=db_username
        self.DB_PASS=db_password
        self.DB_NAME=db_name



