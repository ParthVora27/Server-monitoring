# -*- coding: utf-8 -*-
import json
import os
import boto3
from botocore.exceptions import ClientError

def load_metrics_from_json(platform):
    try:
        bucket_name = os.environ["bucket_name"]
        s3 = boto3.client('s3')
        file_name = 'windows.json' if platform.lower() == 'windows' else 'linux.json'

        # Read the JSON file from the S3 bucket
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        metrics_data = json.loads(response['Body'].read().decode('utf-8'))

        return metrics_data
    except ClientError as e:
        print(f"Error loading metrics from {file_name}: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise


def get_dashboard(client, dashboard_name):
    try:
        response = client.get_dashboard(DashboardName=dashboard_name)
        dashboard_body = json.loads(response['DashboardBody'])
        return dashboard_body
    except Exception as e:
        print(f"Error fetching dashboard {dashboard_name}: {str(e)}")
        raise


def get_or_create_widget(widgets, region, metric_title, metric_stat, metric_period):
    widget_title = f"{region} {metric_title}"
    # Look for an existing widget
    for widget in widgets:
        if widget['type'] == 'metric' and widget['properties']['title'] == widget_title:
            return widget

    # If not found, create a new widget
    new_widget = {
        "type": "metric",
        "properties": {
            "metrics": [],
            "period": metric_period,
            "stat": metric_stat,
            "region": region,
            "title": widget_title
        }
    }
    widgets.append(new_widget)
    print(f"Created new widget for {region} {metric_title}")
    return new_widget


def is_instance_present_in_widget(widget, instance_id):
    '''
    This function iterates through the widget data and return a boolean value if instance is already present in the widgets
    '''
    if 'properties' in widget:
        properties = widget['properties']
        if 'metrics' in properties:
            metrics = properties['metrics']
            for metric in metrics:
                if instance_id in metric:
                    return True

    return False


def add_instance_metrics_to_widget(instance_id, account_id, region, platform, client, dashboard_name):
    try:
        # Load metrics from the correct JSON file based on platform
        metrics_data = load_metrics_from_json(platform)

        # Get the current dashboard
        dashboard_body = get_dashboard(client, dashboard_name)

        variables = dashboard_body.get('variables', [])
        widgets = dashboard_body.get('widgets', [])

        # Iterate over the metrics data to add metrics to the correct widget
        for metric in metrics_data:
            region = region  # Assume region is always provided in the metrics_data
            metric_name = metric['metric_name']
            metric_title = metric['title']
            metric_stat = metric['stat']
            metric_period = metric['period']
            # Find or create the widget for the specific region and metric
            widget = get_or_create_widget(widgets, region, metric_title, metric_stat, metric_period)
            if is_instance_present_in_widget(widget, instance_id):
                continue
            # Append the new instance's metrics to the widget
            new_metric = [
                metric['namespace'], metric['metric_name'], "InstanceId", instance_id, {"accountId": str(account_id)}
            ]
            widget['properties']['metrics'].append(new_metric)
            print(f"Added instance {instance_id} to widget for {region} {metric_name}")

        # Update the dashboard with the modified widgets array
        updated_dashboard_body = {
            "variables": variables,
            "widgets": widgets
        }

        # Update the dashboard with the modified widget
        response = client.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=json.dumps(updated_dashboard_body)
        )
        print(f"Updated dashboard with new instance {instance_id}. Response: {response}")

    except Exception as e:
        print(f"Error adding instance {instance_id} to dashboard {dashboard_name}: {str(e)}")
        raise


def remove_instance_from_widget(cloudwatch_client, dashboard_name, instance_id):
    try:
        # Get the current dashboard
        dashboard_body = get_dashboard(cloudwatch_client, dashboard_name)

        variables = dashboard_body.get('variables', [])
        widgets = dashboard_body.get('widgets', [])

        # Iterate over widgets to find and remove the instance's metrics
        updated_widgets = []
        for widget in widgets:
            if widget['type'] == 'metric':
                # Remove any metric for the given instance_id_to_remove
                updated_metrics = [
                    metric for metric in widget['properties']['metrics']
                    if not (metric[2] == 'InstanceId' and metric[3] == instance_id)
                ]

                # If the widget still has metrics after removing the instance, keep it
                if updated_metrics:
                    widget['properties']['metrics'] = updated_metrics
                    #updated_widgets.append(widget)
                else:
                    print(f"Removing widget {widget['properties']['title']} as it has no instances left.")

        # Update the dashboard with only the widgets that still have metrics
        updated_dashboard_body = {
            "variables": variables,
            "widgets": widgets
        }

        # Update the dashboard with the modified widgets
        response = cloudwatch_client.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=json.dumps(updated_dashboard_body)
        )
        print(f"Updated dashboard after removing instance {instance_id}. Response: {response}")

    except Exception as e:
        print(f"Error removing instance {instance_id} from dashboard {dashboard_name}: {str(e)}")
        raise


# Alarm code added
def get_metric_title_from_json(platform):
    """
    Extract metric tittle from the json file based on the platform
    """
    metric_data = load_metrics_from_json(platform)
    metric_title = {metric['title'] for metric in metric_data}
    return metric_title


def is_alarm_present_in_widget(widget, alarm_arn):
    """
    Check if alarm is already present in the widget
    """
    for alarm in widget['properties']['alarms']:
        if alarm == alarm_arn:
            return True
    return False


def create_or_fetch_alarm_widget(widgets, region):
    """
      Find or create an alarm widget
    """
    widget_title = f"{region} Alarms"
    # Checks if the widget already exists
    for widget in widgets:
        if widget['type'] == 'alarm' and widget['properties']['title'] == widget_title:
            return widget
    # Creates a new widget if it doesn't exist
    new_alarm_widget = {
        "type": "alarm",
        "properties": {
            "alarms": [],
            "title": widget_title,
            "states": [
                "ALARM"
            ]
        }
    }
    widgets.append(new_alarm_widget)
    print(f"Created new alarm widget for {region}")
    return new_alarm_widget


def get_and_add_alarms_to_widget(region, cloudwatch_client, dashboard_name, platform, instance_id):
    """
    Fetch and add active alarms to the widget
    """
    metric_titles = get_metric_title_from_json(platform)
    # active_alarm_arns = fetch_alarms(region,cloudwatch_client)
    if not metric_titles:
        print(f"No active alarms found in {region}")
        return

    # fetch all alarms int current region
    describe_alarms_response = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'],
                                                                 AlarmNamePrefix=instance_id)
    instance_alarm_arns = []
    if "MetricAlarms" in describe_alarms_response and len(describe_alarms_response["MetricAlarms"]) > 0:
        metric_alarms = describe_alarms_response["MetricAlarms"]
        for metric_alarm in metric_alarms:
            instance_alarm_arns.append(metric_alarm["AlarmArn"])
    if len(instance_alarm_arns) > 0:
        add_alarms_to_widgets(instance_alarm_arns, region, cloudwatch_client, dashboard_name, platform, instance_id)


def add_alarms_to_widgets(alarm_arns, region, cloudwatch_client, dashboard_name, platform, instance_id):
    """
     Manages alarms in the dashboard
    """
    # Extract metric title based on platform

    # fetch existing widgets from the dashboard
    dashboard_body = get_dashboard(cloudwatch_client, dashboard_name)

    variables = dashboard_body.get('variables', [])

    widgets = dashboard_body.get('widgets', [])
    widget = create_or_fetch_alarm_widget(widgets, region)

    # Add matching alarm arn to widget if not already present
    for alarm_arn in alarm_arns:
        if not is_alarm_present_in_widget(widget, alarm_arns):
            widget['properties']['alarms'].append(alarm_arn)

    updated_dashboard_body = {
        "variables": variables,
        "widgets": widgets
    }
    print(f"Updated dashboard alarm widgets with value: {widgets}")

    try:
        response = cloudwatch_client.put_dashboard(DashboardName=dashboard_name,
                                                   DashboardBody=json.dumps(updated_dashboard_body))
        print(f"Updated dashboard for {region}. Response: {response}")
    except Exception as e:
        print(f"Error updating dashboard {dashboard_name}: {str(e)}")


def remove_alarm_from_widget(cloudwatch_client, region, dashboard_name, platform, instance_id):
    # Fetch current dashboard body
    try:
        metric_titles = [metric['title'] for metric in load_metrics_from_json(platform)]
        dashboard_body = get_dashboard(cloudwatch_client, dashboard_name)
        variables = dashboard_body.get('variables', [])
        widgets = dashboard_body.get('widgets', [])
        updated_widgets = []
        instance_alarm_arns = []
        for widget in widgets:
            widget_title = f'{region} Alarms'
            if widget['type'] == 'alarm' and widget["properties"]["title"] == widget_title:
                describe_alarms_response = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'],
                                                                             AlarmNamePrefix=instance_id)
                if "MetricAlarms" in describe_alarms_response and len(describe_alarms_response["MetricAlarms"]) > 0:
                    metric_alarms = describe_alarms_response["MetricAlarms"]
                    for metric_alarm in metric_alarms:
                        instance_alarm_arns.append(metric_alarm["AlarmArn"])
                updated_alarms_list = [i for i in widget["properties"]["alarms"] if i not in instance_alarm_arns]
                if len(updated_alarms_list) > 0:
                    widget["properties"]["alarms"] = updated_alarms_list
                else:
                    print(f"Removing widget {widget['properties']['alarms']}  no active alarm left")
                    widgets.remove(widget)
                break

        updated_dashboard_body = {
            "variables": variables,
            "widgets": widgets
        }
        print(f"Updated dashboard alarm widgets with value: {widgets}")
        response = cloudwatch_client.put_dashboard(DashboardName=dashboard_name,
                                                   DashboardBody=json.dumps(updated_dashboard_body))
        print(f"Updated dashboard after removing deleted alarms. Response: {response}")
    except Exception as e:
        print(f"Error updating dashboard {dashboard_name} for region {region} : {str(e)}")
        raise
