# -*- coding: utf-8 -*-
import boto3
import json


# dynamodb operation delete record
def handle_instance_termination(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
                                account_id):
    print("instance state change to terminated , instance-id : ", instance_id)
    response = client_dynamodb.delete_item(
        TableName=dynamodb_table,
        Key={
            db_partition_key: {
                'S': instance_id
            },
            db_sort_key: {
                'N': account_id
            }
        }
    )
    print("Dynamodb Record Removed")
