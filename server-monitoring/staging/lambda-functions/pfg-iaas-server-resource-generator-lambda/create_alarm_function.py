# -*- coding: utf-8 -*-
from create_update_instance_metrics import load_metrics_from_json
import boto3
from datetime import datetime, timedelta
import time  # Import time module for sleep functionality

metrics_data = None


# Create metric alarms
def create_alarms(monitoring_account_id, cloudwatch_client, instance_id, account_id, instance_region,
                  sns_topic_create_ticket, sns_topic_close_ticket, platform):
    # Load metrics from the correct JSON file based on platform
    metrics = load_metrics_from_json(platform)

    for metric in metrics:
        # Default dimensions: InstanceId
        dimensions = [{"Name": "InstanceId", "Value": instance_id}]

        if 'dimensions' in metric:
            for dimension in metric['dimensions']:
                dimensions.append({
                    "Name": dimension['name'],
                    "Value": dimension['value']
                })

        # Set missing data treatment
        if 'TreatMissingData' in metric:
            missingdata = metric['TreatMissingData']
        else:
            missingdata = 'breaching'

        # Filter account based on metric type
        if metric['metric_name'] == "ec2_heartbeat_service":
            account_id_filter = monitoring_account_id
        else:
            account_id_filter = account_id

        # Windows : Specific logic for "LogicalDisk % Free Space"
        if metric['metric_name'] == "LogicalDisk % Free Space":
            # Filter metrics by InstanceId for Windows
            disk_list_metrics = cloudwatch_client.list_metrics(
                MetricName=metric['metric_name'],
                Namespace=metric["namespace"],
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],  # Filter by InstanceId
                IncludeLinkedAccounts=True
            )
            print("LIST METRICS (Windows):", disk_list_metrics)

            # Extract dimensions from the disk_list_metrics response for LogicalDisk % Free Space
            for metric_data in disk_list_metrics['Metrics']:
                # Extracting dimensions
                metric_dimensions = metric_data['Dimensions']
                print("Dimensions from list_metrics (Windows):", metric_dimensions)

                # Check if dimensions include both 'objectname' and 'instance'
                has_required_dimensions = any(d['Name'] == 'objectname' for d in metric_dimensions) and any(
                    d['Name'] == 'instance' for d in metric_dimensions)

                if has_required_dimensions:
                    # Find the 'instance' value from dimensions to use in alarm name
                    instance_value = next((d['Value'] for d in metric_dimensions if d['Name'] == 'instance'), None)
                    if instance_value:
                        # Find the InstanceId value from dimensions
                        instance_id_value = next((d['Value'] for d in metric_dimensions if d['Name'] == 'InstanceId'),
                                                 instance_id)

                        # Update alarm_name to match the desired format:
                        alarm_name = f"{instance_id_value}:{metric['title']}:{instance_value}:{account_id}:{instance_region}"

                        # Create the alarm using the dynamic dimensions
                        cloudwatch_client.put_metric_alarm(
                            AlarmName=alarm_name,
                            EvaluationPeriods=metric['datapoints'],
                            Threshold=metric['threshold'],
                            ComparisonOperator=metric['comparisonOperator'],
                            Metrics=[{
                                "Id": "m1",
                                "MetricStat": {
                                    "Metric": {
                                        'Namespace': metric["namespace"],
                                        'MetricName': metric["metric_name"],
                                        'Dimensions': metric_dimensions  # Use dynamic dimensions here
                                    },
                                    'Period': metric["period"],
                                    'Stat': metric['stat']
                                },
                                'AccountId': account_id_filter
                            }],
                            OKActions=[sns_topic_close_ticket],
                            AlarmActions=[sns_topic_create_ticket],
                            Tags=[{'Key': 'AccountId', 'Value': account_id_filter}],
                            TreatMissingData=missingdata
                        )

                        print(
                            f"Created alarm for Windows LogicalDisk % Free Space: {alarm_name} with dimensions: {metric_dimensions}")
                else:
                    print(f"Skipping Windows metric with missing required dimensions: {metric_dimensions}")

        # Linux : Specific logic for "disk_used_percent"
        elif metric['metric_name'] == "disk_used_percent":
            # Filter metrics by InstanceId for Linux
            disk_list_metrics = cloudwatch_client.list_metrics(
                MetricName=metric['metric_name'],
                Namespace=metric["namespace"],
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],  # Filter by InstanceId
                IncludeLinkedAccounts=True
            )
            print("LIST METRICS (Linux):", disk_list_metrics)

            # Extract dimensions for disk_used_percent (Linux)
            for metric_data in disk_list_metrics['Metrics']:
                metric_dimensions = metric_data['Dimensions']
                print("Dimensions from list_metrics (Linux):", metric_dimensions)

                # Check if dimensions include 'path', 'device', 'fstype', and 'InstanceId'
                has_required_dimensions = any(d['Name'] == 'path' for d in metric_dimensions) and \
                                          any(d['Name'] == 'device' for d in metric_dimensions) and \
                                          any(d['Name'] == 'fstype' for d in metric_dimensions) and \
                                          any(d['Name'] == 'path' for d in metric_dimensions) and \
                                          any(d['Name'] == 'InstanceId' for d in metric_dimensions)

                if has_required_dimensions:
                    # Extract the necessary dimension values
                    path_value = next((d['Value'] for d in metric_dimensions if d['Name'] == 'path'), None)
                    device_value = next((d['Value'] for d in metric_dimensions if d['Name'] == 'device'), None)
                    fstype_value = next((d['Value'] for d in metric_dimensions if d['Name'] == 'fstype'), None)
                    path_value = next((d['Value'] for d in metric_dimensions if d['Name'] == 'path'), None)
                    instance_id_value = next((d['Value'] for d in metric_dimensions if d['Name'] == 'InstanceId'), None)

                    # Create the alarm using the dynamic dimensions
                    alarm_name = f"{instance_id}:{metric['title']}:{path_value}:{account_id}:{instance_region}"

                    # Determine if the 'fstype' is 'xfs' or 'ext4' and adjust the alarm accordingly
                    if fstype_value not in ['xfs', 'ext4']:
                        print(f"Unsupported fstype: {fstype_value}. Only 'xfs' and 'ext4' are supported.")
                    else:
                        # If 'fstype' is either 'xfs' or 'ext4', proceed with alarm creation
                        # Create the alarm using the dynamic dimensions
                        alarm_name = f"{instance_id}:{metric['title']}:{path_value}:{account_id}:{instance_region}"

                        # Create the alarm using the dynamic dimensions
                        cloudwatch_client.put_metric_alarm(
                            AlarmName=alarm_name,
                            EvaluationPeriods=metric['datapoints'],
                            Threshold=metric['threshold'],
                            ComparisonOperator=metric['comparisonOperator'],
                            Metrics=[{
                                "Id": "m1",
                                "MetricStat": {
                                    "Metric": {
                                        'Namespace': metric["namespace"],
                                        'MetricName': metric["metric_name"],
                                        'Dimensions': metric_dimensions  # Use dynamic dimensions here
                                    },
                                    'Period': metric["period"],
                                    'Stat': metric['stat']
                                },
                                'AccountId': account_id_filter
                            }],
                            OKActions=[sns_topic_close_ticket],
                            AlarmActions=[sns_topic_create_ticket],
                            Tags=[{'Key': 'AccountId', 'Value': account_id_filter}],
                            TreatMissingData=missingdata
                        )

                        print(
                            f"Created alarm for Linux disk_used_percent: {alarm_name} with dimensions: {metric_dimensions}")
                else:
                    print(f"Skipping Linux metric with missing required dimensions: {metric_dimensions}")
        else:
            # If it's not LogicalDisk % Free Space or disk_used_percent, create alarm as normal without needing list_metrics
            alarm_name = f"{instance_id}:{metric['title']}:{account_id}:{instance_region}"

            cloudwatch_client.put_metric_alarm(
                AlarmName=alarm_name,
                EvaluationPeriods=metric['datapoints'],
                Threshold=metric['threshold'],
                ComparisonOperator=metric['comparisonOperator'],
                Metrics=[{
                    "Id": "m1",
                    "MetricStat": {
                        "Metric": {
                            'Namespace': metric["namespace"],
                            'MetricName': metric["metric_name"],
                            'Dimensions': dimensions  # Standard dimensions for non-LogicalDisk metrics
                        },
                        'Period': metric["period"],
                        'Stat': metric['stat']
                    },
                    'AccountId': account_id_filter
                }],
                OKActions=[sns_topic_close_ticket],
                AlarmActions=[sns_topic_create_ticket],
                Tags=[{'Key': 'AccountId', 'Value': account_id_filter}],
                TreatMissingData=missingdata
            )

            print(f"Created alarm: {alarm_name} with dimensions: {dimensions}")
