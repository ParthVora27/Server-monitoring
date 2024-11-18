# -*- coding: utf-8 -*-
import boto3
import json


# dynamodb operation add record
def handle_instance_running(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
                            account_id, instance_state, db_instance_status, db_instance_monitoring,
                            db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_platform, db_instance_platform):
    print("instance state change to running , instance-id : ", instance_id)
    #  # Prepare the EBS volume IDs for DynamoDB
    # ebs_volume_ids_dynamodb = {
    #     "L": [{"S": volume_id} for volume_id in ebs_volume_ids]  # Properly formatted list of EBS IDs
    # } if ebs_volume_ids else {"L": []}

    response = client_dynamodb.put_item(
        TableName=dynamodb_table,
        Item={
            db_partition_key: {
                'S': instance_id
            },
            db_sort_key: {
                'N': account_id
            },
            db_instance_status: {
                'S': instance_state
            },
            db_instance_monitoring: {
                'S': instance_tag
            },
            db_instance_region: {
                'S': instance_region
            },
            db_instance_timestamp: {
                'S': instance_timestamp
            },
            db_instance_platform: {
                'S': instance_platform
            }
        }
    )
    print("DynamoDB Record Added")
