# -*- coding: utf-8 -*-
from sys import platform
import boto3
import json
import os
import traceback

from create_update_instance_metrics import add_instance_metrics_to_widget
from create_update_instance_metrics import remove_instance_from_widget
from create_update_instance_metrics import get_and_add_alarms_to_widget
from create_update_instance_metrics import remove_alarm_from_widget
from create_alarm_function import create_alarms
from delete_alarm_function import handle_instance_termination
from disable_alarm_function import handle_stop_instance
from disable_alarm_function import handle_tag_change
from ec2_client import get_ec2_client
from cw_widget import manage_dashboards

# Get environment variables
sns_topic_create_ticket = os.environ.get("sns_topic_create_ticket")
sns_topic_close_ticket = os.environ.get("sns_topic_close_ticket")
dashboard_name = os.environ.get("dashboard_name")
account_dashboard_name = os.environ.get("account_dashboard_name")
monitoring_account_id = os.environ.get("monitoring_account")
tag_key_to_check = os.environ.get("pfg_instance_schedule")
sqs_queue_url = os.environ.get("sqs_url_alarm_creation")

# Ensure environment variables are set
if not sns_topic_create_ticket or not sns_topic_close_ticket or not dashboard_name or not account_dashboard_name or not monitoring_account_id or not tag_key_to_check or not sqs_queue_url:
    raise ValueError("One or more environment variables are missing.")


def lambda_handler(event, context):
    # Custom widget dashboard management
    manage_dashboards()

    print('Received event:', json.dumps(event))

    # Check if the event is from DynamoDB Streams or SQS
    if 'Records' in event:
        for record in event['Records']:
            if 'body' in record:  # SQS event
                process_sqs_message(record)
            elif 'dynamodb' in record:  # DynamoDB event
                process_dynamodb_record(record)
            else:
                print("Unsupported event type.")
    else:
        print("No records found in event")


# Function to process SQS messages
def process_sqs_message(record):
    # Extract the SQS message body
    sqs_message = json.loads(record['body'])
    print(f"Processing SQS message: {json.dumps(sqs_message)}")

    try:
        # Check if the message contains the DynamoDB record
        if 'dynamodb' in sqs_message:
            # Extract the DynamoDB record from the SQS message
            instance_status = sqs_message['dynamodb']  # The whole message contains the record

            # Extract necessary fields from DynamoDB record (using NewImage)
            account_id = instance_status['NewImage']['Account_Id']['N']
            instance_id = instance_status['NewImage']['Instance_Id']['S']
            instance_region = instance_status['NewImage']['Region']['S']  # Region field is inside NewImage
            cloudwatch_client = boto3.client('cloudwatch', region_name=instance_region)

            # Log extracted fields (for debugging purposes)
            print(f"Account ID: {account_id}, Instance ID: {instance_id}, Region: {instance_region}")

            # Call the handle_instance_insert function to process the insert
            handle_instance_insert(instance_status, cloudwatch_client, instance_id, instance_region, account_id)

        else:
            print("The SQS message does not contain a valid DynamoDB record.")

        # After processing, delete the message from SQS
        delete_message_from_sqs(record['receiptHandle'])

    except Exception as e:
        print(f"Error processing message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")


# Function to delete the message from SQS
def delete_message_from_sqs(receipt_handle):
    try:
        sqs_client = boto3.client('sqs')
        response = sqs_client.delete_message(
            QueueUrl=sqs_queue_url,
            ReceiptHandle=receipt_handle
        )
        print(f"Message deleted from SQS: {response}")
    except Exception as e:
        print(f"Error deleting message from SQS: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")


def process_dynamodb_record(record):
    # Extract DynamoDB record
    instance_status = record['dynamodb']

    # Check for necessary keys
    if 'Keys' not in instance_status or 'Account_Id' not in instance_status['Keys'] or 'Instance_Id' not in \
            instance_status['Keys']:
        print("Missing necessary keys in DynamoDB record.")
        return

    account_id = instance_status['Keys']['Account_Id']['N']
    instance_id = instance_status['Keys']['Instance_Id']['S']
    instance_region = record['awsRegion']
    cloudwatch_client = boto3.client('cloudwatch', region_name=instance_region)

    # Process events based on the event type
    if record['eventName'] == "REMOVE":
        handle_instance_removal(instance_status, cloudwatch_client, instance_id, instance_region, account_id)

    elif record['eventName'] == "INSERT":
        # Send DynamoDB record to SQS
        send_to_sqs(instance_status)

    elif record['eventName'] == "MODIFY":
        handle_instance_modify(instance_status, cloudwatch_client, instance_id, instance_region, account_id)

    else:
        print(f"Unsupported event type: {record['eventName']}")


def handle_instance_removal(instance_status, cloudwatch_client, instance_id, instance_region, account_id):
    print("Instance terminated - deleting all alarms")
    ec2_client = get_ec2_client(account_id, instance_region)
    ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_info = ec2_response['Reservations'][0]['Instances'][0]
    instance_platform = instance_info.get('Platform', 'Linux')
    print(f"Instance {instance_id} platform: {instance_platform}")

    remove_instance_from_widget(cloudwatch_client, dashboard_name, instance_id)
    remove_instance_from_widget(cloudwatch_client, account_dashboard_name, instance_id)
    remove_alarm_from_widget(cloudwatch_client, instance_region, dashboard_name, instance_platform, instance_id)
    remove_alarm_from_widget(cloudwatch_client, instance_region, account_dashboard_name, instance_platform, instance_id)
    handle_instance_termination(cloudwatch_client, instance_id, account_id)


def handle_instance_insert(instance_status, cloudwatch_client, instance_id, instance_region, account_id):
    print(f"Handling INSERT event for instance: {instance_id}")

    # Describe EC2 instance to identify its platform
    ec2_client = get_ec2_client(account_id, instance_region)
    ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_info = ec2_response['Reservations'][0]['Instances'][0]
    instance_platform = instance_info.get('Platform', 'Linux')
    print(f"Instance {instance_id} platform: {instance_platform}")

    # Ensure that 'Instance Status' and 'Monitoring' keys exist in the NewImage
    if 'Instance Status' in instance_status['NewImage'] and 'Monitoring' in instance_status['NewImage']:
        db_instance_status = instance_status['NewImage']['Instance Status']['S']
        print("Instance Status: ", db_instance_status)

        db_instance_monitoring = instance_status['NewImage']['Monitoring']['S']
        print("Instance Monitoring Tag: ", db_instance_monitoring)

        if db_instance_status == "running" and db_instance_monitoring == "enabled":
            print("instance running - create alarm & update dashboard")
            create_alarms(monitoring_account_id, cloudwatch_client, instance_id, account_id, instance_region,
                          sns_topic_create_ticket, sns_topic_close_ticket, instance_platform)

            add_instance_metrics_to_widget(instance_id, account_id, instance_region, platform, cloudwatch_client,
                                           dashboard_name)
            add_instance_metrics_to_widget(instance_id, account_id, instance_region, platform, cloudwatch_client,
                                           account_dashboard_name)
            get_and_add_alarms_to_widget(instance_region, cloudwatch_client, dashboard_name, instance_platform,
                                         instance_id)
            get_and_add_alarms_to_widget(instance_region, cloudwatch_client, account_dashboard_name, instance_platform,
                                         instance_id)


        elif db_instance_status == "running" and db_instance_monitoring == "enabled,suppressed":
            print(f"Monitor tag 'Enabled,suppressed' for instance {instance_id}, disable instance alarm actions")
            create_alarms(monitoring_account_id, cloudwatch_client, instance_id, account_id, instance_region,
                          sns_topic_create_ticket, sns_topic_close_ticket, instance_platform)
            handle_tag_change(instance_id, cloudwatch_client)

            add_instance_metrics_to_widget(instance_id, account_id, instance_region, platform, cloudwatch_client,
                                           dashboard_name)
            add_instance_metrics_to_widget(instance_id, account_id, instance_region, platform, cloudwatch_client,
                                           account_dashboard_name)
            get_and_add_alarms_to_widget(instance_region, cloudwatch_client, dashboard_name, instance_platform,
                                         instance_id)
            get_and_add_alarms_to_widget(instance_region, cloudwatch_client, account_dashboard_name, instance_platform,
                                         instance_id)


        elif db_instance_status == "running" and db_instance_monitoring == "disabled":
            print("instance tag disabled - delete all alarm")
            remove_alarm_from_widget(cloudwatch_client, instance_region, dashboard_name, instance_platform, instance_id)
            remove_alarm_from_widget(cloudwatch_client, instance_region, account_dashboard_name, instance_platform,
                                     instance_id)
            remove_instance_from_widget(cloudwatch_client, dashboard_name, instance_id)
            remove_instance_from_widget(cloudwatch_client, account_dashboard_name, instance_id)
            handle_instance_termination(cloudwatch_client, instance_id, account_id)

        elif db_instance_status == "stopped":
            print("instance stopped - disable alarm except heartbeat")
            handle_stop_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check)
        else:
            print("No relevant instance status or instance monitoring found")
    else:
        print("No 'Instance Status' or 'Monitoring' found in DynamoDB record.")


def handle_instance_modify(instance_status, cloudwatch_client, instance_id, instance_region, account_id):
    print(f"Handling MODIFY event for instance: {instance_id}")

    # Describe EC2 instance to identify its platform
    ec2_client = get_ec2_client(account_id, instance_region)
    ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_info = ec2_response['Reservations'][0]['Instances'][0]
    instance_platform = instance_info.get('Platform', 'Linux')
    print(f"Instance {instance_id} platform: {instance_platform}")

    if 'Instance Status' in instance_status['NewImage'] and 'Monitoring' in instance_status['NewImage']:
        db_instance_status = instance_status['NewImage']['Instance Status']['S']
        print("Instance Status: ", db_instance_status)

        db_instance_monitoring = instance_status['NewImage']['Monitoring']['S']
        print("Instance Monitoring Tag: ", db_instance_monitoring)

        if db_instance_status == "running" and db_instance_monitoring == "enabled":
            print("instance running - create alarm & update dashboard")
            create_alarms(monitoring_account_id, cloudwatch_client, instance_id, account_id, instance_region,
                          sns_topic_create_ticket, sns_topic_close_ticket, instance_platform)

            add_instance_metrics_to_widget(instance_id, account_id, instance_region, platform, cloudwatch_client,
                                           dashboard_name)
            add_instance_metrics_to_widget(instance_id, account_id, instance_region, platform, cloudwatch_client,
                                           account_dashboard_name)
            get_and_add_alarms_to_widget(instance_region, cloudwatch_client, dashboard_name, instance_platform,
                                         instance_id)
            get_and_add_alarms_to_widget(instance_region, cloudwatch_client, account_dashboard_name, instance_platform,
                                         instance_id)


        elif db_instance_status == "running" and db_instance_monitoring == "enabled,suppressed":
            print(f"Monitor tag 'Enabled,suppressed' for instance {instance_id}, disable instance alarm actions")
            create_alarms(monitoring_account_id, cloudwatch_client, instance_id, account_id, instance_region,
                          sns_topic_create_ticket, sns_topic_close_ticket, instance_platform)
            handle_tag_change(instance_id, cloudwatch_client)

            add_instance_metrics_to_widget(instance_id, account_id, instance_region, platform, cloudwatch_client,
                                           dashboard_name)
            add_instance_metrics_to_widget(instance_id, account_id, instance_region, platform, cloudwatch_client,
                                           account_dashboard_name)
            get_and_add_alarms_to_widget(instance_region, cloudwatch_client, dashboard_name, instance_platform,
                                         instance_id)
            get_and_add_alarms_to_widget(instance_region, cloudwatch_client, account_dashboard_name, instance_platform,
                                         instance_id)


        elif db_instance_status == "running" and db_instance_monitoring == "disabled":
            print("instance tag disabled - delete all alarm")
            remove_alarm_from_widget(cloudwatch_client, instance_region, dashboard_name, instance_platform, instance_id)
            remove_alarm_from_widget(cloudwatch_client, instance_region, account_dashboard_name, instance_platform,
                                     instance_id)
            remove_instance_from_widget(cloudwatch_client, dashboard_name, instance_id)
            remove_instance_from_widget(cloudwatch_client, account_dashboard_name, instance_id)
            handle_instance_termination(cloudwatch_client, instance_id, account_id)

        elif db_instance_status == "stopped":
            print("instance stopped - disable alarm except heartbeat")
            handle_stop_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check)
        else:
            print("No relevant instance status or instance monitoring found")
    else:
        print("No 'Instance Status' or 'Monitoring' found in DynamoDB record.")


def send_to_sqs(instance_status):
    """ Send DynamoDB record to SQS """
    try:
        sqs_client = boto3.client('sqs')
        message_body = json.dumps({
            "dynamodb": instance_status
        })

        response = sqs_client.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=message_body
        )

        print(f"Message sent to SQS: {response}")
    except Exception as e:
        print(f"Error sending message to SQS: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
