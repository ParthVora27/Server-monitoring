# -*- coding: utf-8 -*-
import boto3
import json

# DynamoDB operation update record
def handle_instance_stopped(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
        account_id, instance_state, db_instance_status, db_instance_monitoring, db_instance_region, instance_region,
        instance_tag, instance_timestamp, db_instance_timestamp, instance_platform, db_instance_platform):
    print("Instance state changed to stopped, instance-id: ", instance_id)

    response = client_dynamodb.update_item(
        TableName=dynamodb_table,
        Key={
            db_partition_key: {
                'S': instance_id
            },
            db_sort_key: {
                'N': account_id
            }
        },
        ExpressionAttributeNames={
            '#Instance_Status': db_instance_status,
            '#Instance_Timestamp': db_instance_timestamp,
            '#Instance_Monitoring': db_instance_monitoring,
            '#Instance_Region': db_instance_region,
            '#Instance_Platform': db_instance_platform

        },
        ExpressionAttributeValues={
            ':State': {
                'S': instance_state,
            },
            ':Timestamp': {
                'S': str(instance_timestamp),
            },
            ':Monitoring': {
                'S': instance_tag,
            },
            ':Region': {
                'S': instance_region,
            },
            ':Platform': {
                'S': instance_platform,
            }
        },
        UpdateExpression='SET #Instance_Status = :State, #Instance_Timestamp = :Timestamp, #Instance_Monitoring = :Monitoring, #Instance_Region = :Region, #Instance_Platform = :Platform',
    )

    print("DynamoDB Record Updated")
    # return response  # Return the response for further use or debugging





# # -*- coding: utf-8 -*-
# import boto3
# import json


# # dynamodb operation update record
# def handle_instance_stopped(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#         account_id, instance_state, db_instance_status, db_instance_monitoring, db_instance_region, instance_region,
#         instance_tag, instance_timestamp, db_instance_timestamp):
#     print("instance state change to stopped , instance-id : ", instance_id)
#     response = client_dynamodb.update_item(
#         TableName=dynamodb_table,
#         Key={
#             db_partition_key: {
#                 'S': instance_id
#             },
#             db_sort_key: {
#                 'N': account_id
#             }
#         },
#         ExpressionAttributeNames={
#             '#Instance_Status': db_instance_status,
#             '#Instance_Timestamp': db_instance_timestamp,
#             '#Instance_Monitoring': db_instance_monitoring,
#             '#Instance_Region': db_instance_region,
#         },
#         ExpressionAttributeValues={
#             ':State': {
#                 'S': instance_state,
#             },
#             ':Timestamp': {
#                 'S': instance_timestamp,
#             },
#             ':Monitoring': {
#                 'S': instance_tag,
#             },
#             ':Region': {
#                 'S': instance_region,
#             },
#         },
#         UpdateExpression='SET #Instance_Status = :State, #Instance_Timestamp = :Timestamp', #Instance_Monitoring = :Monitoring', #Instance_Region = :Region',
#     )

#     print("Dynamodb Record Updated")
