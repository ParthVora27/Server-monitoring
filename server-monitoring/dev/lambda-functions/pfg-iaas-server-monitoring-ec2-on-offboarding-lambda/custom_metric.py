# -*- coding: utf-8 -*-
import boto3
import json


def custom_metric(client_cloudwatch, instance_id, instance_timestamp, instance_state):
    state_value_map = {
        'running': 0,
        'stopped': 1
    }

    client_cloudwatch.put_metric_data(
        Namespace='EC2HeartBeatService',
        MetricData=[
            {
                'MetricName': "ec2_heartbeat_service",
                'Timestamp': instance_timestamp,
                'Value': state_value_map[instance_state],
                'Dimensions': [
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    }
                ],
            },
        ]
    )

    print("custom metric added for instance-id : ", instance_id)


## TAG CHANGE CUSTOM METRIC

def custom_metric_tag_change(client_cloudwatch, instance_id, instance_timestamp, instance_tag):

    if 'enabled' in instance_tag:
        client_cloudwatch.put_metric_data(
            Namespace='EC2HeartBeatService',
            MetricData=[
                {
                    'MetricName': "ec2_heartbeat_service",
                    'Timestamp': instance_timestamp,
                    'Value': 0,
                    'Dimensions': [
                        {
                            'Name': 'InstanceId',
                            'Value': instance_id
                        }
                    ],
                },
            ]
        )

        print("tag change - custom metric added for instance-id : ", instance_id)
