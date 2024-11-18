# -*- coding: utf-8 -*-
import boto3
import json

client = boto3.client('cloudwatch')

def lambda_handler(event, context):
    response = client.describe_alarms()

    ok_alarm_count = 0
    in_alarm_count = 0
    insufficient_data_alarm_count = 0
    ok_alarm_name = []
    in_alarm_name = []
    insufficient_data_alarm_name = []

    for alarms in response['MetricAlarms']:
        alarm_state = alarms['StateValue']
        alarm_name = alarms['AlarmName']
        if alarm_state == 'OK':
            ok_alarm_count += 1
            ok_alarm_name.append(alarm_name)
        elif alarm_state == 'ALARM':
            in_alarm_count += 1
            in_alarm_name.append(alarm_name)
        elif alarm_state == 'INSUFFICIENT_DATA':
            insufficient_data_alarm_count += 1
            insufficient_data_alarm_name.append(alarm_name)

    with open('widget.html', 'r') as file:
        cw_html_file = file.read()

    cw_html_file = cw_html_file.replace('{{ok_alarm_count}}', str(ok_alarm_count))
    cw_html_file = cw_html_file.replace('{{in_alarm_count}}', str(in_alarm_count))
    cw_html_file = cw_html_file.replace('{{insufficient_data_alarm_count}}', str(insufficient_data_alarm_count))

    region = "us-west-2"

    def create_options(alarm_names):
        if not alarm_names:
            return ""  # Return an empty string if there are no alarms
        return "".join([
            f'<option value="https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/Alarms/{alarm_name}">{alarm_name}</option>'
            for alarm_name in alarm_names
        ])

    ok_alarm_name_options = create_options(ok_alarm_name)
    in_alarm_name_options = create_options(in_alarm_name)
    insufficient_data_alarm_name_options = create_options(insufficient_data_alarm_name)

    # Prepare the placeholders for HTML
    cw_html_file = cw_html_file.replace('{{ok_alarm_name}}', f'<select class="alarm-select">{ok_alarm_name_options}</select>' if ok_alarm_name else 'No Alarms')
    cw_html_file = cw_html_file.replace('{{in_alarm_name}}', f'<select class="alarm-select">{in_alarm_name_options}</select>' if in_alarm_name else 'No Alarms')
    cw_html_file = cw_html_file.replace('{{insufficient_data_alarm_name}}', f'<select class="alarm-select">{insufficient_data_alarm_name_options}</select>' if insufficient_data_alarm_name else 'No Alarms')

    return cw_html_file









# import boto3
# import json
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger()

# DOCS = """
# ## Echo
# This script retrieve all the alarms within a region. This includes alarms in Ok, ALARM, INSUFFICIENT_DATA state
# ### Widget parameters
# Param | Description
# ---|---
# **region** | AWS Region
# """

# def create_options(alarm_names):
#     if len(alarm_names) == 0:
#         alarm_names = ["None"]
#     return "".join([f"<option text-align=\"left\">{alarm_name}</option>" for alarm_name in alarm_names])


# def lambda_handler(event, context):
#     if 'describe' in event:
#         return DOCS

#     aws_region = event["region"]
#     client = boto3.client("cloudwatch", region_name=aws_region)
#     response = client.describe_alarms()
#     ok_alarm_count = 0
#     in_alarm_count = 0
#     insufficient_data_alarm_count = 0
#     ok_alarm_name = []
#     in_alarm_name = []
#     insufficient_data_alarm_name = []

#     for alarms in response["MetricAlarms"]:
#         alarm_state = alarms["StateValue"]
#         alarm_name = alarms["AlarmName"]
#         if alarm_state == "OK":
#             ok_alarm_count += 1
#             ok_alarm_name.append(alarm_name)
#         elif alarm_state == "ALARM":
#             in_alarm_count += 1
#             in_alarm_name.append(alarm_name)
#         elif alarm_state == "INSUFFICIENT_DATA":
#             insufficient_data_alarm_count += 1
#             insufficient_data_alarm_name.append(alarm_name)

#     with open("widget.html", "r") as file:
#         alarms_history_file = file.read()

#     alarms_history_file = alarms_history_file.replace("{{ok_alarm_count}}", str(ok_alarm_count))
#     alarms_history_file = alarms_history_file.replace("{{in_alarm_count}}", str(in_alarm_count))
#     alarms_history_file = alarms_history_file.replace("{{insufficient_data_alarm_count}}",
#                                                       str(insufficient_data_alarm_count))

#     ok_alarm_name_options = create_options(ok_alarm_name)
#     in_alarm_name_options = create_options(in_alarm_name)
#     insufficient_data_alarm_name_options = create_options(insufficient_data_alarm_name)

#     alarms_history_file = alarms_history_file.replace("{{ok_alarm_name}}", ok_alarm_name_options)
#     alarms_history_file = alarms_history_file.replace("{{in_alarm_name}}", in_alarm_name_options)
#     alarms_history_file = alarms_history_file.replace("{{insufficient_data_alarm_name}}",
#                                                       insufficient_data_alarm_name_options)

#     return alarms_history_file
