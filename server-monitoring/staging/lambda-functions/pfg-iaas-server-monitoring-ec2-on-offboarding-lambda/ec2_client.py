# -*- coding: utf-8 -*-
import boto3

def get_role_arn(account_id):
    return f'arn:aws:iam::{account_id}:role/pfg-iaas-server-cw-dashboard-cross-account-role'


# Create assume role for source account
def assume_role(account_id):
    sts = boto3.client('sts')
    role_arn = get_role_arn(account_id)
    response =  sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName = 'LambdaAssumeRoleSession'
    )
    return response['Credentials']


# Get all Instance details from source accounts
def get_ec2_client(account_id, region):
    try:
        credentials = assume_role(account_id)
        ec2 = boto3.client('ec2',region_name =region,
                            aws_access_key_id=credentials['AccessKeyId'],
                            aws_secret_access_key=credentials['SecretAccessKey'],
                            aws_session_token = credentials['SessionToken'])
        return ec2
    except Exception as e:
        print(e)
