# -*- coding: utf-8 -*-
import boto3
from decimal import Decimal
import os

Monitoring = "Monitoring"
InstanceStatus = "Instance Status"
table_name = os.environ["dynamodb_table_name"] ##'pfg-iaas-server-ec2-monitoring'

def lambda_handler(event, context):
    print("Event received:", event)

    aws_region = event["region"]
    # Initialize DynamoDB resource and client
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    client = boto3.client('dynamodb')

    table = dynamodb.Table(table_name)

    # Describe the table to get metadata including the primary key
    table_description = client.describe_table(TableName=table_name)
    print("Table Description:", table_description)

    # Extract primary key (partition key)
    key_schema = table_description['Table']['KeySchema']

    # Find the partition key (the primary key we are interested in)
    partition_key = None
    for key in key_schema:
        if key['KeyType'] == 'HASH':
            partition_key = key['AttributeName']

    if not partition_key:
        return {
            'statusCode': 500,
            'body': 'Unable to determine partition key',
            'headers': {'Content-Type': 'text/html'}
        }

    # Extract accountId from the event params
    account_id = event['accountId']
    print("Extracted accountId:", account_id)

    # Scan the table to get all items
    response = table.scan()
    items = response['Items']
    print("Items fetched from DynamoDB:", items)

    # Filter items based on account ID if provided
    if account_id and account_id != '${accountId}':
        items = [item for item in items if str(item.get('Account_Id', None)) == str(account_id)]
        print(f"Filtered items for account {account_id}:", items)
    else:
        items = response['Items']
        print(f"Filtered items for account {account_id}:", items)

    # Use the partition key for instance IDs
    instance_ids = [item.get(partition_key, "No instance") for item in items]
    total_instance_count = len(instance_ids)
    print("Total instance count:", total_instance_count)

    monitored_enabled_instance_count = sum(1 for item in items if item.get(Monitoring) == 'enabled')
    monitored_suppressed_instance_count = sum(1 for item in items if item.get(Monitoring) == 'enabled,suppressed')
    monitored_disabled_instance_count = sum(1 for item in items if item.get(Monitoring) == 'disabled')

    # New counters for running and stopped EC2 instances
    running_ec2_count = sum(1 for item in items if item.get(InstanceStatus) == 'running')
    stopped_ec2_count = sum(1 for item in items if item.get(InstanceStatus) == 'stopped')

    # Generate the HTML table with headers
    html_table = "<table border='1'>"
    html_table += "<tr><th>EC2 Details</th><th>Count</th><th>Instance ID</th></tr>"
    html_table += f"<tr><td>Total EC2</td><td>{total_instance_count}</td><td>{generate_instance_dropdown(instance_ids)}</td></tr>"
    html_table += f"<tr><td>Running EC2</td><td>{running_ec2_count}</td><td>{generate_instance_dropdown(get_instance_ids_by_status(items, 'running', partition_key))}</td></tr>"
    html_table += f"<tr><td>Stopped EC2</td><td>{stopped_ec2_count}</td><td>{generate_instance_dropdown(get_instance_ids_by_status(items, 'stopped', partition_key))}</td></tr>"
    html_table += f"<tr><td>EC2 Tag: Enabled</td><td>{monitored_enabled_instance_count}</td><td>{generate_instance_dropdown(get_instance_ids_by_tag(items, 'enabled', partition_key))}</td></tr>"
    html_table += f"<tr><td>EC2 Tag: Suppressed</td><td>{monitored_suppressed_instance_count}</td><td>{generate_instance_dropdown(get_instance_ids_by_tag(items, 'enabled,suppressed', partition_key))}</td></tr>"
    html_table += f"<tr><td>EC2 Tag: Disabled</td><td>{monitored_disabled_instance_count}</td><td>{generate_instance_dropdown(get_instance_ids_by_tag(items, 'disabled', partition_key))}</td></tr>"
    html_table += "</table>"

    # Return the HTML table
    return html_table

def generate_instance_dropdown(instance_ids):
    if not instance_ids or all(id == "No instance" for id in instance_ids):
        return "No Instance"

    dropdown = "<select>"
    for instance_id in instance_ids:
        dropdown += f"<option value='{instance_id}'>{instance_id}</option>"
    dropdown += "</select>"
    return dropdown

def get_instance_ids_by_status(items, status, partition_key):
    return [item.get(partition_key, "No instance") for item in items if item.get(InstanceStatus) == status]

def get_instance_ids_by_tag(items, tag_value, partition_key):
    return [item.get(partition_key, "No instance") for item in items if item.get(Monitoring) == tag_value]



# import boto3

# Monitoring = "Monitoring"
# InstanceStatus = "Instance Status"
# table_name = 'pfg-iaas-server-ec2-monitoring'


# def lambda_handler(event, context):
#     aws_region = event["region"]
#     # Initialize DynamoDB resource and client
#     dynamodb = boto3.resource('dynamodb', region_name=aws_region)
#     client = boto3.client('dynamodb')

#     table = dynamodb.Table(table_name)

#     # Describe the table to get metadata including the primary key
#     table_description = client.describe_table(TableName=table_name)

#     # Extract primary key (partition key)
#     key_schema = table_description['Table']['KeySchema']

#     # Find the partition key (the primary key we are interested in)
#     partition_key = None
#     for key in key_schema:
#         if key['KeyType'] == 'HASH':
#             partition_key = key['AttributeName']

#     if not partition_key:
#         return {
#             'statusCode': 500,
#             'body': 'Unable to determine partition key',
#             'headers': {'Content-Type': 'text/html'}
#         }

#     # Scan the table to get all items
#     response = table.scan()

#     # Extract the values of the primary key (partition key) and Monitoring status
#     items = response['Items']

#     instance_ids = [item[partition_key] for item in items]
#     total_instance_count = len(instance_ids)

#     monitored_enabled_instance_count = sum(1 for item in items if item.get(Monitoring) == 'enabled')
#     monitored_suppressed_instance_count = sum(1 for item in items if item.get(Monitoring) == 'enabled,suppressed')
#     monitored_disabled_instance_count = sum(1 for item in items if item.get(Monitoring) == 'disabled')

#     # New counters for running and stopped EC2 instances
#     running_ec2_count = sum(1 for item in items if item.get(InstanceStatus) == 'running')
#     stopped_ec2_count = sum(1 for item in items if item.get(InstanceStatus) == 'stopped')

#     # Generate the HTML table with headers
#     html_table = "<table border='1'>"
#     html_table += "<tr><th>EC2 Details</th><th>Count</th></tr>"
#     html_table += f"<tr><td>Total EC2</td><td>{total_instance_count}</td></tr>"
#     html_table += f"<tr><td>Running EC2</td><td>{running_ec2_count}</td></tr>"
#     html_table += f"<tr><td>Stopped EC2</td><td>{stopped_ec2_count}</td></tr>"
#     html_table += f"<tr><td>EC2 Tag : Enabled</td><td>{monitored_enabled_instance_count}</td></tr>"
#     html_table += f"<tr><td>EC2 Tag : Suppressed</td><td>{monitored_suppressed_instance_count}</td></tr>"
#     html_table += f"<tr><td>EC2 Tag : Disabled</td><td>{monitored_disabled_instance_count}</td></tr>"
#     html_table += "</table>"

#     # Return the HTML table
#     return html_table
