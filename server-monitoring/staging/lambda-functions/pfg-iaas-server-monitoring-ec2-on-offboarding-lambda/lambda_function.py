# -*- coding: utf-8 -*-
import boto3
import json
import os

from custom_metric import custom_metric
from custom_metric import custom_metric_tag_change
from instance_start import handle_instance_running
from instance_stop import handle_instance_stopped
from instance_tag_change import handle_instance_tag_changed
from instance_terminate import handle_instance_termination
from ec2_client import get_ec2_client

#TODO ADD EBS VOLUME
dynamodb_table = os.environ["dynamodb_table_name"]
db_partition_key = os.environ["dynamodb_table_partition_key"]
db_sort_key = os.environ["dynamodb_table_sort_key"]
db_instance_status = "Instance Status"
db_instance_monitoring = "Monitoring"
db_instance_region = "Region"
db_instance_timestamp = "TimeStamp"
db_instance_platform = "Platform"

client_dynamodb = boto3.client('dynamodb')
client_cloudwatch = boto3.client('cloudwatch')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table)


def remove_entry_from_dynamodb(instance_id, account_id):
    try:
        table.delete_item(
            Key={
                db_partition_key: instance_id,
                db_sort_key: int(account_id)
            }
        )
        print(
            f"Removed entry from Dynamodb OR Not Added entry in Dynamodb as Monitoring Tag missing for instance {instance_id}.")
    except Exception as e:
        print(f"Error in removing or not adding monitoring tag entry in Dynamodb: {e}")


def lambda_handler(event, context):
    print('Received event:', json.dumps(event))

    detail_type = event['detail-type']
    print('Event type :', detail_type)

    account_id = event['account']
    instance_region = event['region']
    instance_timestamp = event['time']

    if detail_type == "EC2 Instance State-change Notification":
        instance_state = event['detail']['state']
        instance_id = event['detail']['instance-id']

        # Describe EC2 instance to identify its platform
        ec2_client = get_ec2_client(account_id, instance_region)
        ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_describe = ec2_response['Reservations'][0]['Instances'][0]

        # Get tags from the instance
        instance_tag = None
        for tag in instance_describe.get('Tags', []):
            if tag['Key'] == 'pfg-server-monitoring':
                instance_tag = tag['Value']

        # Check if instance_tag is missing or empty
        if instance_tag is None or instance_tag == "":
            remove_entry_from_dynamodb(instance_id, account_id)
        else:
            # Process the instance based on its state
            if instance_state == "terminated":
                handle_instance_termination(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
                                            account_id)
            elif instance_state == "running":
                custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
                handle_instance_running(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
                                        account_id, instance_state, db_instance_status, db_instance_monitoring,
                                        db_instance_region, instance_region, instance_tag, instance_timestamp,
                                        db_instance_timestamp, instance_describe.get('Platform', 'Linux'),
                                        db_instance_platform)
            elif instance_state == "stopped":
                custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
                handle_instance_stopped(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
                                        account_id, instance_state, db_instance_status, db_instance_monitoring,
                                        db_instance_region, instance_region, instance_tag, instance_timestamp,
                                        db_instance_timestamp, instance_describe.get('Platform', 'Linux'),
                                        db_instance_platform)
            else:
                print("Instance in pending event found")

    elif detail_type == "Tag Change on Resource":
        resources = event["resources"][0]
        resource = resources.split('/', 1)
        instance_id = resource[1]

        # Describe EC2 instance to identify its platform
        ec2_client = get_ec2_client(account_id, instance_region)
        ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_describe = ec2_response['Reservations'][0]['Instances'][0]

        # Get tags from the instance
        instance_tag = None
        for tag in instance_describe.get('Tags', []):
            if tag['Key'] == 'pfg-server-monitoring':
                instance_tag = tag['Value']

        # Check if instance_tag is missing or empty
        if instance_tag is None or instance_tag == "":
            remove_entry_from_dynamodb(instance_id, account_id)
        else:
            dynamodb_table_items = table.get_item(
                Key={
                    db_partition_key: instance_id,
                    db_sort_key: int(account_id)
                }
            )

            if 'Item' in dynamodb_table_items:
                print(dynamodb_table_items)
                custom_metric_tag_change(client_cloudwatch, instance_id, instance_timestamp, instance_tag)
                handle_instance_tag_changed(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
                                            account_id, instance_tag, db_instance_monitoring, instance_timestamp,
                                            db_instance_timestamp)
            else:
                print("DynamoDB Table does not contain Instance Id :", instance_id)
                print("Adding DynamoDB record for Instance Id :", instance_id)

                # Get the state and platform of the instance
                instance_state = instance_describe['State']['Name']
                print(f"Instance {instance_id} state: {instance_state}")

                instance_platform = instance_describe.get('Platform', 'Linux')
                print(f"Instance {instance_id} platform: {instance_platform}")

                # EBS Volume IDs
                ebs_volume_ids = [ebs['Ebs']['VolumeId'] for ebs in instance_describe.get('BlockDeviceMappings', [])]
                print("EBS Volume IDs attached to the instance:", ebs_volume_ids)

                if instance_state == "running":
                    custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
                    handle_instance_running(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
                                            account_id, instance_state, db_instance_status, db_instance_monitoring,
                                            db_instance_region, instance_region, instance_tag, instance_timestamp,
                                            db_instance_timestamp, instance_platform, db_instance_platform)
                elif instance_state == "stopped":
                    custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
                    handle_instance_stopped(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
                                            account_id, instance_state, db_instance_status, db_instance_monitoring,
                                            db_instance_region, instance_region, instance_tag, instance_timestamp,
                                            db_instance_timestamp, instance_platform, db_instance_platform)
                else:
                    print("Instance in pending event found")

    else:
        print("No relevant event found")

# # -*- coding: utf-8 -*-
# import boto3
# import json
# import os

# from custom_metric import custom_metric
# from custom_metric import custom_metric_tag_change
# from instance_start import handle_instance_running
# from instance_stop import handle_instance_stopped
# from instance_tag_change import handle_instance_tag_changed
# from instance_terminate import handle_instance_termination
# from ec2_client import get_ec2_client

# dynamodb_table = os.environ["dynamodb_table_name"]
# db_partition_key = os.environ["dynamodb_table_partition_key"]
# db_sort_key = os.environ["dynamodb_table_sort_key"]
# db_instance_status = "Instance Status"
# db_instance_monitoring = "Monitoring"
# db_instance_region = "Region"
# db_instance_timestamp = "TimeStamp"
# db_instance_platform = "Platform"

# client_dynamodb = boto3.client('dynamodb')
# client_cloudwatch = boto3.client('cloudwatch')

# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table(dynamodb_table)


# def remove_entry_from_dynamodb(instance_id, account_id):
#     try:
#         table.delete_item(
#             Key={
#                 db_partition_key: instance_id,
#                 db_sort_key: int(account_id)
#             }
#         )
#         print(f"Monitoring Tag missing - for instance {instance_id} from DynamoDB.")
#     except Exception as e:
#         print(f"Monitoring Tag missing - Error : {e}")


# def lambda_handler(event, context):
#     print('Received event:', json.dumps(event))

#     detail_type = event['detail-type']
#     print('Event type :', detail_type)

#     account_id = event['account']
#     instance_region = event['region']
#     instance_timestamp = event['time']

#     if detail_type == "EC2 Instance State-change Notification":
#         instance_state = event['detail']['state']
#         instance_id = event['detail']['instance-id']

#         # Describe EC2 instance to identify its platform
#         ec2_client = get_ec2_client(account_id, instance_region)
#         ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
#         instance_describe = ec2_response['Reservations'][0]['Instances'][0]

#         # Get tags from the instance
#         instance_tag = None
#         for tag in instance_describe.get('Tags', []):
#             if tag['Key'] == 'pfg-server-monitoring':
#                 instance_tag = tag['Value']

#         if instance_tag is None:
#             remove_entry_from_dynamodb(instance_id, account_id)
#         else:
#             # Process the instance based on its state
#             if instance_state == "terminated":
#                 handle_instance_termination(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                             account_id)
#             elif instance_state == "running":
#                 custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
#                 handle_instance_running(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                         account_id, instance_state, db_instance_status, db_instance_monitoring,
#                                         db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_describe.get('Platform', 'Linux'), db_instance_platform)
#             elif instance_state == "stopped":
#                 custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
#                 handle_instance_stopped(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                         account_id, instance_state, db_instance_status, db_instance_monitoring,
#                                         db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_describe.get('Platform', 'Linux'), db_instance_platform)
#             else:
#                 print("Instance in pending event found")

#     elif detail_type == "Tag Change on Resource":
#         resources = event["resources"][0]
#         resource = resources.split('/', 1)
#         instance_id = resource[1]

#         # Describe EC2 instance to identify its platform
#         ec2_client = get_ec2_client(account_id, instance_region)
#         ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
#         instance_describe = ec2_response['Reservations'][0]['Instances'][0]

#         # Get tags from the instance
#         instance_tag = None
#         for tag in instance_describe.get('Tags', []):
#             if tag['Key'] == 'pfg-server-monitoring':
#                 instance_tag = tag['Value']

#         if instance_tag is None:
#             remove_entry_from_dynamodb(instance_id, account_id)
#         else:
#             dynamodb_table_items = table.get_item(
#                 Key={
#                     db_partition_key: instance_id,
#                     db_sort_key: int(account_id)
#                 }
#             )

#             if 'Item' in dynamodb_table_items:
#                 print(dynamodb_table_items)
#                 custom_metric_tag_change(client_cloudwatch, instance_id, instance_timestamp, instance_tag)
#                 handle_instance_tag_changed(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                             account_id, instance_tag, db_instance_monitoring, instance_timestamp, db_instance_timestamp)
#             else:
#                 print("DynamoDB Table does not contain Instance Id :", instance_id)
#                 print("Adding DynamoDB record for Instance Id :", instance_id)

#                 # Get the state and platform of the instance
#                 instance_state = instance_describe['State']['Name']
#                 print(f"Instance {instance_id} state: {instance_state}")

#                 instance_platform = instance_describe.get('Platform', 'Linux')
#                 print(f"Instance {instance_id} platform: {instance_platform}")

#                 # EBS Volume IDs
#                 ebs_volume_ids = [ebs['Ebs']['VolumeId'] for ebs in instance_describe.get('BlockDeviceMappings', [])]
#                 print("EBS Volume IDs attached to the instance:", ebs_volume_ids)

#                 if instance_state == "running":
#                     custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
#                     handle_instance_running(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                             account_id, instance_state, db_instance_status, db_instance_monitoring,
#                                             db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_platform, db_instance_platform)
#                 elif instance_state == "stopped":
#                     custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
#                     handle_instance_stopped(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                             account_id, instance_state, db_instance_status, db_instance_monitoring,
#                                             db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_platform, db_instance_platform)
#                 else:
#                     print("Instance in pending event found")

#     else:
#         print("No relevant event found")


# # -*- coding: utf-8 -*-
# import boto3
# import json
# import os

# from custom_metric import custom_metric
# from custom_metric import custom_metric_tag_change
# from instance_start import handle_instance_running
# from instance_stop import handle_instance_stopped
# from instance_tag_change import handle_instance_tag_changed
# from instance_terminate import handle_instance_termination
# from ec2_client import get_ec2_client

# dynamodb_table = os.environ["dynamodb_table_name"]  # "test-parth-pgs-monitoring"
# db_partition_key = os.environ["dynamodb_table_partition_key"]  # "Instance_Id"
# db_sort_key = os.environ["dynamodb_table_sort_key"]  # "Account_Id"
# db_instance_status = "Instance Status"
# db_instance_monitoring = "Monitoring"
# db_instance_region = "Region"
# db_instance_timestamp = "TimeStamp"
# db_instance_platform = "Platform"
# # db_instance_volume = "EBS Volumes"

# client_dynamodb = boto3.client('dynamodb')
# client_cloudwatch = boto3.client('cloudwatch')

# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table(dynamodb_table)


# def lambda_handler(event, context):
#     print('Received event:', json.dumps(event))

#     detail_type = event['detail-type']
#     print('Event type :', detail_type)

#     account_id = event['account']
#     instance_region = event['region']
#     instance_timestamp = event['time']

#     # instance_tag = 'enabled'
#     # instance_volume = event['detail']['state']

#     if detail_type == "EC2 Instance State-change Notification":
#         instance_state = event['detail']['state']
#         instance_id = event['detail']['instance-id']

#         # Describe EC2 instance to identify it's platform
#         ec2_client = get_ec2_client(account_id, instance_region)
#         ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
#         instance_describe = ec2_response['Reservations'][0]['Instances'][0]

#         # Get tags from the instance
#         instance_tag_key = instance_describe.get('Tags', [])
#         instance_tag = "missing"
#         for tag in instance_tag_key:
#             if tag['Key'] == 'pfg-server-monitoring':
#                 instance_tag = tag['Value']

#         # platform
#         instance_platform = instance_describe.get('Platform', 'Linux')
#         print(f"Instance {instance_id} platform: {instance_platform}")

#         # Extracting EBS volume IDs
#         ebs_volume_ids = []
#         if 'BlockDeviceMappings' in instance_describe:
#             ebs_volume_ids = [ebs['Ebs']['VolumeId'] for ebs in instance_describe['BlockDeviceMappings']]
#         print("EBS Volume IDs attached to the instance:", ebs_volume_ids)


#         if instance_state == "terminated":
#             # invoke terminate lambda
#             handle_instance_termination(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                         account_id)
#         elif instance_state == "running":
#             # custom metric
#             custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
#             # invoke running lambda
#             handle_instance_running(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                     account_id, instance_state, db_instance_status, db_instance_monitoring,
#                                     db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_platform, db_instance_platform)
#         elif instance_state == "stopped":
#             custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
#             # invoke stop lambda
#             handle_instance_stopped(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                     account_id, instance_state, db_instance_status, db_instance_monitoring,
#                                     db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_platform, db_instance_platform)
#         else:
#             print("Instance in pending event found")


#     elif detail_type == "Tag Change on Resource":
#         # fetching tag values
#         resources = event["resources"][0]
#         resource = resources.split('/', 1)
#         instance_id = resource[1]

#         # Describe EC2 instance to identify it's platform
#         ec2_client = get_ec2_client(account_id, instance_region)
#         ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
#         instance_describe = ec2_response['Reservations'][0]['Instances'][0]

#         # Get tags from the instance
#         instance_tag_key = instance_describe.get('Tags', [])
#         instance_tag = "missing"
#         for tag in instance_tag_key:
#             if tag['Key'] == 'pfg-server-monitoring':
#                 instance_tag = tag['Value']
#         # instance_tag = event["detail"]["tags"]["pfg-server-monitoring"]
#         # instance_timestamp = event['time']

#         dynamodb_table_items = table.get_item(
#             Key={
#                 'Instance_Id': instance_id,
#                 'Account_Id': int(account_id)
#             }
#         )

#         if 'Item' in dynamodb_table_items:
#             print(dynamodb_table_items)

#             custom_metric_tag_change(client_cloudwatch, instance_id, instance_timestamp, instance_tag)
#             # invoke instance tag change lambda
#             handle_instance_tag_changed(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                     account_id, instance_tag, db_instance_monitoring, instance_timestamp, db_instance_timestamp)
#         else:
#             print("Dynamodb Table does not contain Instance Id :", instance_id)

#             print("Adding Dynamodb record for Instance Id :", instance_id)

#             # Describe EC2 instance to identify it's platform
#             ec2_client = get_ec2_client(account_id, instance_region)
#             ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
#             instance_describe = ec2_response['Reservations'][0]['Instances'][0]

#             # instance state
#             instance_state = instance_describe['State']['Name']
#             print(f"Instance {instance_id} state: {instance_state}")

#             # platform
#             instance_platform = instance_describe.get('Platform', 'Linux')
#             print(f"Instance {instance_id} platform: {instance_platform}")

#             # Extracting EBS volume IDs
#             ebs_volume_ids = []
#             if 'BlockDeviceMappings' in instance_describe:
#                 ebs_volume_ids = [ebs['Ebs']['VolumeId'] for ebs in instance_describe['BlockDeviceMappings']]
#             print("EBS Volume IDs attached to the instance:", ebs_volume_ids)


#             if instance_state == "running":
#                 # custom metric
#                 custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
#                 # invoke running lambda
#                 handle_instance_running(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                     account_id, instance_state, db_instance_status, db_instance_monitoring,
#                                     db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_platform, db_instance_platform)
#             elif instance_state == "stopped":
#                 custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state)
#                 # invoke stop lambda
#                 handle_instance_stopped(client_dynamodb, dynamodb_table, db_partition_key, instance_id, db_sort_key,
#                                     account_id, instance_state, db_instance_status, db_instance_monitoring,
#                                     db_instance_region, instance_region, instance_tag, instance_timestamp, db_instance_timestamp, instance_platform, db_instance_platform)
#             else:
#                 print("Instance in pending event found")


#     else:
#         print("No relevant event found")
