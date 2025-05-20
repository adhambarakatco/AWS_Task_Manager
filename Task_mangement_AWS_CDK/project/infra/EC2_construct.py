from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)
from constructs import Construct


class EC2InstanceConstruct(Construct):
    def __init__(
            self,
            scope: Construct,
            id: str,
            *,
            vpc: ec2.Vpc,
            ec2_role=None,
            **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        self.security_group = ec2.SecurityGroup(
            self, "InstanceSG",
            vpc=vpc,
            description=f"Security group for {id}",
            allow_all_outbound=True
        )

        # More secure SSH configuration - restrict to specific IP or use SSM instead
        # Replace 'YOUR_IP_ADDRESS' with your actual IP or remove this rule and use SSM
        # self.security_group.add_ingress_rule(
        #     peer=ec2.Peer.ipv4('0.0.0.0/0'),  # Consider restricting this to your IP
        #     connection=ec2.Port.tcp(22),
        #     description="Allow SSH access from specific IPs"
        # )

        self.security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP access"
        )

        # Add HTTPS support
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS access"
        )

        # Use the IAM role if provided, otherwise create a default one
        if not ec2_role:
            ec2_role = iam.Role(
                self, "EC2Role",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
                ]
            )

        self.instance = ec2.Instance(
            self, id,
            instance_type=ec2.InstanceType("t3.micro"),  # Using t2.micro which is free tier eligible
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=self.security_group,
            role=ec2_role
        )

        # Add user data to install required software
        self.instance.add_user_data(
            "#!/bin/bash",
            "yum update -y",
            "yum install -y httpd",
            "systemctl start httpd",
            "systemctl enable httpd",
            "yum install -y git",
            "yum install -y python3 python3-pip",
            "echo 'Hello from Task Management System' > /var/www/html/index.html",
            "curl -sL https://rpm.nodesource.com/setup_14.x | bash -",
            "yum install -y nodejs",
            "mkdir -p /home/ec2-user/task-manager",
            "chown -R ec2-user:ec2-user /home/ec2-user/task-manager"
        )



