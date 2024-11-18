# -*- coding: utf-8 -*-
import boto3
import json


# Delete alarms
def handle_instance_termination(cloudwatch_client, instance_id, account_id):
    metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
    for alarm in metric_alarms['MetricAlarms']:
        print(alarm)
        if instance_id in alarm['AlarmName']:
            cloudwatch_client.delete_alarms(AlarmNames=[alarm['AlarmName']])
            print(f"Deleted metric alarm {alarm['AlarmName']}")
        else:
            print(f"{alarm['AlarmName']} Metric alarm does not contain instance id : {instance_id}")
