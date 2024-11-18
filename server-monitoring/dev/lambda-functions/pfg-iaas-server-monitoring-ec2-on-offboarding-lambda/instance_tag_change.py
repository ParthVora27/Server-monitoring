# -*- coding: utf-8 -*-
import boto3
import json

# Instance tag disable - keep DynamoDB value and delete all alarms
# Instance tag enabled, suppressed - keep DynamoDB value and delete all alarms except heartbeat alarm
def handle_instance_tag_changed(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key, account_id,
                                tagValue, db_instance_monitoring, instance_timestamp, db_instance_timestamp):
    print("Instance tag change, instance-id: ", instance_id, "\nTag change: ", tagValue)

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
            '#Instance_Monitoring': db_instance_monitoring,
            '#Instance_Timestamp': db_instance_timestamp,
        },
        ExpressionAttributeValues={
            ':Tag': {
                'S': tagValue,
            },
            ':Timestamp': {
                'S': instance_timestamp,
            },
        },
        UpdateExpression='SET #Instance_Monitoring = :Tag, #Instance_Timestamp = :Timestamp',
    )

    print("DynamoDB Record Updated")




# # -*- coding: utf-8 -*-
# import boto3
# import json


# # instance tag disable - keep dynamodb value and delete all alarm
# # instance tag enabled,supressed - keep dynamodb value and delete all alarm except heartbeat alarm
# def handle_instance_tag_changed(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key, account_id,
#                                 tagValue, db_instance_monitoring, instance_timestamp, db_instance_timestamp):
#     print("instance tag change , instance-id : ", instance_id, "\n" "tag change : ", tagValue)
#     if tagValue == "disabled":
#         response = client_dynamodb.update_item(
#             TableName=dynamodb_table,
#             Key={
#                 db_partition_key: {
#                     'S': instance_id
#                 },
#                 db_sort_key: {
#                     'N': account_id
#                 }
#             },
#             ExpressionAttributeNames={
#                 '#Instance_Monitoring': db_instance_monitoring,
#             },
#             ExpressionAttributeValues={
#                 ':Tag': {
#                     'S': tagValue,
#                 },
#             },
#             UpdateExpression='SET #Instance_Monitoring = :Tag',
#         )
#         print("Dynamodb Record Updated")

#     elif tagValue == "enabled,suppressed":
#         response = client_dynamodb.update_item(
#             TableName=dynamodb_table,
#             Key={
#                 db_partition_key: {
#                     'S': instance_id
#                 },
#                 db_sort_key: {
#                     'N': account_id
#                 }
#             },
#             ExpressionAttributeNames={
#                 '#Instance_Monitoring': db_instance_monitoring,
#             },
#             ExpressionAttributeValues={
#                 ':Tag': {
#                     'S': tagValue,
#                 },
#             },
#             UpdateExpression='SET #Instance_Monitoring = :Tag',
#         )
#         print("Dynamodb Record Updated")

#     elif tagValue == "enabled":
#         response = client_dynamodb.update_item(
#             TableName=dynamodb_table,
#             Key={
#                 db_partition_key: {
#                     'S': instance_id
#                 },
#                 db_sort_key: {
#                     'N': account_id
#                 }
#             },
#             ExpressionAttributeNames={
#                 '#Instance_Monitoring': db_instance_monitoring,
#             },
#             ExpressionAttributeValues={
#                 ':Tag': {
#                     'S': tagValue,
#                 },
#             },
#             UpdateExpression='SET #Instance_Monitoring = :Tag',
#         )
#         print("Dynamodb Record Updated")

#     else:
#         print("No proper updated tag")
