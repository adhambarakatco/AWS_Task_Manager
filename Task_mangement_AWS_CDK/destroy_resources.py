#!/usr/bin/env python3
import os
import boto3
import time
from botocore.exceptions import ClientError

# Initialize clients
ec2 = boto3.client('ec2')
rds = boto3.client('rds')
cloudformation = boto3.client('cloudformation')


def delete_vpc_resources():
    """Delete VPC and all dependent resources"""
    # Get all VPCs
    print("Finding VPCs...")
    response = ec2.describe_vpcs()

    for vpc in response['Vpcs']:
        vpc_id = vpc['VpcId']
        print(f"Processing VPC: {vpc_id}")

        # 1. Delete Network Interfaces
        try:
            print(f"Finding network interfaces in VPC {vpc_id}...")
            enis = ec2.describe_network_interfaces(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )['NetworkInterfaces']

            for eni in enis:
                eni_id = eni['NetworkInterfaceId']

                # Force detach if attached
                if 'Attachment' in eni:
                    attachment_id = eni['Attachment']['AttachmentId']
                    try:
                        print(f"Force detaching network interface: {eni_id}")
                        ec2.detach_network_interface(
                            AttachmentId=attachment_id,
                            Force=True
                        )
                        # Wait for detachment
                        time.sleep(5)
                    except ClientError as e:
                        print(f"Error detaching network interface {eni_id}: {e}")

                # Delete the network interface
                try:
                    print(f"Deleting network interface: {eni_id}")
                    ec2.delete_network_interface(NetworkInterfaceId=eni_id)
                except ClientError as e:
                    print(f"Error deleting network interface {eni_id}: {e}")
        except ClientError as e:
            print(f"Error processing network interfaces: {e}")

        # 2. Delete VPC Endpoints
        try:
            print(f"Finding VPC endpoints in VPC {vpc_id}...")
            endpoints = ec2.describe_vpc_endpoints(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )['VpcEndpoints']

            if endpoints:
                endpoint_ids = [ep['VpcEndpointId'] for ep in endpoints]
                try:
                    print(f"Deleting VPC endpoints: {endpoint_ids}")
                    ec2.delete_vpc_endpoints(VpcEndpointIds=endpoint_ids)
                except ClientError as e:
                    print(f"Error deleting VPC endpoints: {e}")
        except ClientError as e:
            print(f"Error processing VPC endpoints: {e}")

        # 3. Delete Internet Gateways
        try:
            print(f"Finding internet gateways for VPC {vpc_id}...")
            igws = ec2.describe_internet_gateways(
                Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
            )['InternetGateways']

            for igw in igws:
                igw_id = igw['InternetGatewayId']
                try:
                    print(f"Detaching internet gateway {igw_id} from VPC {vpc_id}")
                    ec2.detach_internet_gateway(
                        InternetGatewayId=igw_id,
                        VpcId=vpc_id
                    )

                    print(f"Deleting internet gateway {igw_id}")
                    ec2.delete_internet_gateway(InternetGatewayId=igw_id)
                except ClientError as e:
                    print(f"Error processing internet gateway {igw_id}: {e}")
        except ClientError as e:
            print(f"Error processing internet gateways: {e}")

        # 4. Delete Subnets
        try:
            print(f"Finding subnets in VPC {vpc_id}...")
            subnets = ec2.describe_subnets(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )['Subnets']

            for subnet in subnets:
                subnet_id = subnet['SubnetId']
                try:
                    print(f"Deleting subnet {subnet_id}")
                    ec2.delete_subnet(SubnetId=subnet_id)
                except ClientError as e:
                    print(f"Error deleting subnet {subnet_id}: {e}")
        except ClientError as e:
            print(f"Error processing subnets: {e}")

        # 5. Delete Security Groups (except default)
        try:
            print(f"Finding security groups in VPC {vpc_id}...")
            sgs = ec2.describe_security_groups(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )['SecurityGroups']

            for sg in sgs:
                # Skip the default security group
                if sg['GroupName'] == 'default':
                    continue

                sg_id = sg['GroupId']
                try:
                    print(f"Deleting security group {sg_id}")
                    ec2.delete_security_group(GroupId=sg_id)
                except ClientError as e:
                    print(f"Error deleting security group {sg_id}: {e}")
        except ClientError as e:
            print(f"Error processing security groups: {e}")

        # 6. Finally try to delete the VPC
        try:
            print(f"Attempting to delete VPC {vpc_id}")
            ec2.delete_vpc(VpcId=vpc_id)
            print(f"Successfully deleted VPC {vpc_id}")
        except ClientError as e:
            print(f"Error deleting VPC {vpc_id}: {e}")


def delete_rds_instances():
    """Delete all RDS instances without final snapshot"""
    try:
        print("Finding RDS instances...")
        response = rds.describe_db_instances()

        for instance in response['DBInstances']:
            db_id = instance['DBInstanceIdentifier']
            try:
                print(f"Modifying RDS instance {db_id} to disable deletion protection")
                # First disable deletion protection
                rds.modify_db_instance(
                    DBInstanceIdentifier=db_id,
                    DeletionProtection=False,
                    ApplyImmediately=True
                )

                # Wait for the modification to complete
                print(f"Waiting for modification to complete...")
                time.sleep(30)

                print(f"Deleting RDS instance {db_id}")
                # Then delete without final snapshot
                rds.delete_db_instance(
                    DBInstanceIdentifier=db_id,
                    SkipFinalSnapshot=True,
                    DeleteAutomatedBackups=True
                )
                print(f"RDS instance {db_id} deletion initiated")
            except ClientError as e:
                print(f"Error deleting RDS instance {db_id}: {e}")
    except ClientError as e:
        print(f"Error listing RDS instances: {e}")


def delete_cloudformation_stacks():
    """Delete all CloudFormation stacks related to ProjectStack"""
    try:
        print("Finding CloudFormation stacks...")
        response = cloudformation.list_stacks(
            StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']
        )

        for stack in response.get('StackSummaries', []):
            stack_name = stack['StackName']
            if 'ProjectStack' in stack_name:
                try:
                    print(f"Deleting CloudFormation stack {stack_name}")
                    cloudformation.delete_stack(StackName=stack_name)
                    print(f"Stack deletion initiated for {stack_name}")
                except ClientError as e:
                    print(f"Error deleting stack {stack_name}: {e}")
    except ClientError as e:
        print(f"Error listing CloudFormation stacks: {e}")


if __name__ == "__main__":
    print("=== AWS Resource Cleanup Script ===")
    print("This will delete AWS resources including RDS instances, VPCs, and CloudFormation stacks.")
    confirmation = input("Type 'DELETE' to confirm: ")

    if confirmation == "DELETE":
        print("Starting cleanup...")
        # Delete in appropriate order
        delete_cloudformation_stacks()
        print("Waiting for CloudFormation operations to begin...")
        time.sleep(30)
        delete_rds_instances()
        print("Waiting for RDS operations to begin...")
        time.sleep(30)
        delete_vpc_resources()
        print("Cleanup process initiated. Check the AWS console for status.")
    else:
        print("Cleanup cancelled.")
