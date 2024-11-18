# -*- coding: utf-8 -*-
import boto3
import os
from datetime import datetime, timedelta


def get_metric_info(accountId, period, instanceId, platform, startTime, endTime, region):
    metricList = ['swap_used_percent', 'mem_used_percent', 'disk_used_percent', 'diskio_read_bytes',
                  'diskio_write_bytes']
    if (platform == 'windows'):
        metricList = ['Paging File % Usage', 'Memory % Committed Bytes In Use', 'Memory Available Bytes',
                      'LogicalDisk % Free Space',
                      'PhysicalDisk Disk Read Bytes/sec', 'PhysicalDisk Disk Write Bytes/sec']
    client = boto3.client('cloudwatch', region_name=region)
    response = client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'id1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'CPUUtilization',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average',
                    'Unit': 'Percent'
                },
                'ReturnData': True,
                'AccountId': accountId
            },
            {
                'Id': 'id2',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'NetworkIn',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average',
                    'Unit': 'Bytes'
                },
                'ReturnData': True,
                'AccountId': accountId
            },
            {
                'Id': 'id3',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'NetworkOut',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average',
                    'Unit': 'Bytes'
                },
                'ReturnData': True,
                'AccountId': accountId
            },
            {
                'Id': 'id4',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'CWAgent',
                        'MetricName': metricList[0],
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average',
                    'Unit': 'Percent'
                },
                'ReturnData': True,
                'AccountId': accountId
            },
            {
                'Id': 'id5',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'CWAgent',
                        'MetricName': metricList[1],
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average',
                    'Unit': 'Percent'
                },
                'ReturnData': True,
                'AccountId': accountId
            },
            {
                'Id': 'id6',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'CWAgent',
                        'MetricName': metricList[2],
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average',
                    'Unit': 'Percent'
                },
                'ReturnData': True,
                'AccountId': accountId
            },
            {
                'Id': 'id7',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'CWAgent',
                        'MetricName': metricList[3],
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average'
                },
                'ReturnData': True,
                'AccountId': accountId
            },
            {
                'Id': 'id8',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'CWAgent',
                        'MetricName': metricList[4],
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instanceId
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average'
                },
                'ReturnData': True,
                'AccountId': accountId
            }
        ],
        StartTime=startTime,
        EndTime=endTime
    )
    return response
