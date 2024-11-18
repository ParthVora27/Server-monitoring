# -*- coding: utf-8 -*-
import json
import os
import boto3
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError

# DynamoDB Table and Key Definitions
TABLE_NAME = os.environ["dynamodb_table_name"]  # 'pfg-iaas-server-ec2-monitoring-us-east-1'
PRIMARY_KEY = os.environ["dynamodb_table_partition_key"]  # 'Instance_Id'
SORT_KEY = os.environ["dynamodb_table_sort_key"]  # 'Account_Id'
PLATFORM_LINUX = 'Linux'
PLATFORM_WINDOWS = 'windows'
TIMESTAMP_ATTR = '#ts'
PARTIAL_ALARM_NAME = 'Disk/Filesystem'


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    cloudwatch = boto3.client('cloudwatch')
    table = dynamodb.Table(TABLE_NAME)

    # Get the current timestamp
    current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Calculate the timestamp for 24 hours ago
    twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    start_time = twenty_four_hours_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
    print(start_time, current_timestamp)

    # Iterate over each record in the event
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        try:
            # Process the file based on its type (Linux or Windows)
            if object_key.lower() == 'linux.json':
                print(f"The uploaded file '{object_key}' is for Linux.")
                platform = PLATFORM_LINUX
            elif object_key.lower() == 'windows.json':
                print(f"The uploaded file '{object_key}' is for Windows.")
                platform = PLATFORM_WINDOWS
            else:
                print(f"The uploaded file '{object_key}' does not match recognized metrics files.")
                continue

            # Scan the DynamoDB table for all instances of the specified platform
            response = table.scan(
                FilterExpression='Platform = :platform',
                ExpressionAttributeValues={':platform': platform}
            )

            instances = response['Items']

            # Update the TimeStamp for each instance
            for instance in instances:
                instance_id = instance[PRIMARY_KEY]
                account_id = instance[SORT_KEY]

                # Update the TimeStamp in DynamoDB
                update_response = table.update_item(
                    Key={PRIMARY_KEY: instance_id, SORT_KEY: account_id},
                    UpdateExpression='SET {} = :val1'.format(TIMESTAMP_ATTR),
                    ExpressionAttributeNames={TIMESTAMP_ATTR: 'TimeStamp'},
                    ExpressionAttributeValues={':val1': current_timestamp}
                )
                print(f"Updated TimeStamp for {platform} instance {instance_id}: {update_response}")

                # Fetch all alarm names from CloudWatch with pagination handling (irrespective of alarm state)
                alarms = []
                next_token = None

                while True:
                    # Fetch alarms without state filter (retrieve all alarms)
                    if next_token:
                        response = cloudwatch.describe_alarms(NextToken=next_token)
                    else:
                        response = cloudwatch.describe_alarms()

                    alarms.extend(response['MetricAlarms'])

                    # Check if there's more data (pagination)
                    next_token = response.get('NextToken')
                    if not next_token:
                        break

                # Now filter alarm names containing the instance_id and the substring "Disk/Filesystem"
                alarms_for_instance = [
                    alarm['AlarmName'] for alarm in alarms
                    if instance_id in alarm['AlarmName'] and PARTIAL_ALARM_NAME in alarm['AlarmName']
                ]

                # For each alarm, check if there are datapoints in the last 24 hours
                if alarms_for_instance:
                    for alarm_name in alarms_for_instance:
                        print(f"Found matching alarm for instance {instance_id}: {alarm_name}")

                        # Retrieve the corresponding alarm details from the 'alarms' list
                        alarm = next((alarm for alarm in alarms if alarm['AlarmName'] == alarm_name), None)

                        if alarm:
                            # Extract metric details for the alarm
                            try:
                                metric_name = alarm['Metrics'][0]['MetricStat']['Metric']['MetricName']
                                namespace = alarm['Metrics'][0]['MetricStat']['Metric']['Namespace']
                                dimensions = alarm['Metrics'][0]['MetricStat']['Metric']['Dimensions']

                                # Query CloudWatch for datapoints in the last 24 hours
                                response = cloudwatch.get_metric_data(
                                    MetricDataQueries=[
                                        {
                                            'Id': 'm1',
                                            'MetricStat': {
                                                'Metric': {
                                                    'Namespace': namespace,
                                                    'MetricName': metric_name,
                                                    'Dimensions': dimensions
                                                },
                                                'Period': 300,
                                                'Stat': 'Average'
                                            },
                                            'AccountId': str(account_id)
                                        }
                                    ],
                                    StartTime=start_time,
                                    EndTime=current_timestamp
                                )

                                # Check if datapoints were returned
                                if not response['MetricDataResults'][0]['Values']:
                                    print(
                                        f"Deleting Alarm: No datapoints found for alarm '{alarm_name}' in the last 24 hours.")
                                    cloudwatch.delete_alarms(AlarmNames=[alarm_name])


                            except KeyError as e:
                                print(f"Error extracting metric details for alarm '{alarm_name}': {e}")
                        else:
                            print(f"Alarm '{alarm_name}' not found in alarms list.")
                else:
                    print(f"No matching alarms found for instance {instance_id}.")

        except ClientError as e:
            print(f"Error accessing file {object_key} in bucket {bucket_name}: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete.')
    }
