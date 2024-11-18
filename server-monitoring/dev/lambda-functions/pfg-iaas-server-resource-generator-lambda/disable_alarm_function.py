# -*- coding: utf-8 -*-
import boto3
import json
from datetime import datetime
import pytz


# Tag change - enabled, suppressed
def handle_tag_change(instance_id, cloudwatch_client):
    metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
    for alarm in metric_alarms['MetricAlarms']:
        if instance_id in alarm['AlarmName']:
            cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
            print(f"Disabled alarm action for alarm: {alarm['AlarmName']}")


def handle_stop_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check):
    # Define a mapping of country codes to time zones
    country_to_timezone = {
        'mex': 'America/Mexico_City',
        'chile': 'America/Santiago',
        'my': 'Asia/Kuala_Lumpur',
        'th': 'Asia/Bangkok'
    }

    # Get the tags
    tags = instance_info.get('Tags', [])
    tag_value = next((tag['Value'] for tag in tags if tag['Key'] == tag_key_to_check), None)

    # If tag is not present, enable heartbeat alarm actions and disable all alarms
    if not tag_value:
        print('Tag is not present. Enabling heartbeat alarm actions for instance:', instance_id)
        disable_all_alarms(instance_id, cloudwatch_client)
        return

    # Extract country, start time, and end time from the tag value
    parts = tag_value.split('-')
    if len(parts) < 6:
        print("Tag value format is incorrect. Expected format: ...-country-environment-start-end")
        print(f"Enabling heartbeat alarm actions for instance: {instance_id}")
        disable_all_alarms(instance_id, cloudwatch_client)
        return

    country_code = parts[2].lower()  # 'mex'
    start_time_str = parts[4]  # '0820'
    end_time_str = parts[5]  # '1840'

    # Validate start and end time strings
    if len(start_time_str) != 4 or len(end_time_str) != 4:
        print("Start or end time format is incorrect. Expected format: HHMM")
        print(f"Enabling heartbeat alarm actions for instance: {instance_id}")
        disable_all_alarms(instance_id, cloudwatch_client)
        return

    # Get the current time for the country's timezone
    current_time = datetime.now(pytz.timezone(country_to_timezone.get(country_code, 'UTC')))
    current_hour = current_time.hour
    current_minute = current_time.minute

    # Convert times to hours and minutes
    start_hour = int(start_time_str[:2])
    start_minute = int(start_time_str[2:])
    end_hour = int(end_time_str[:2])
    end_minute = int(end_time_str[2:])

    # Check if current time is within the specified range
    is_within_range = (
            (start_hour < current_hour or (start_hour == current_hour and start_minute <= current_minute)) and
            (current_hour < end_hour or (current_hour == end_hour and current_minute < end_minute))
    )

    print(f"Current time: {current_time.strftime('%H:%M')}, Is within range: {is_within_range}")

    # Manage alarms based on time range
    metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
    for alarm in metric_alarms['MetricAlarms']:
        if instance_id in alarm['AlarmName']:
            for metrics in alarm['Metrics']:
                metric_service_name = metrics['MetricStat']['Metric']['MetricName']

                # Disable actions for all services except 'ec2_heartbeat_service'
                if 'ec2_heartbeat_service' not in metric_service_name:
                    cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
                    print(f"Disabled alarm actions for alarm: {alarm['AlarmName']}")
                else:
                    # If it's the heartbeat service, manage actions based on time range
                    if is_within_range:
                        cloudwatch_client.enable_alarm_actions(AlarmNames=[alarm['AlarmName']])
                        print(f"Enabled heartbeat alarm actions for alarm: {alarm['AlarmName']}")
                    else:
                        cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
                        print(f"Disabled heartbeat alarm actions for alarm: {alarm['AlarmName']}")

        else:
            print(f"Alarm not found for instance id: {instance_id}")


def disable_all_alarms(instance_id, cloudwatch_client):
    # Disable all alarms for the specified instance except heartbeat alarms
    metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
    for alarm in metric_alarms['MetricAlarms']:
        if instance_id in alarm['AlarmName']:
            for metrics in alarm['Metrics']:
                metric_service_name = metrics['MetricStat']['Metric']['MetricName']
                if 'ec2_heartbeat_service' not in metric_service_name:
                    cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
                    print(f"Disabled alarm actions for alarm: {alarm['AlarmName']}")
                else:
                    cloudwatch_client.enable_alarm_actions(AlarmNames=[alarm['AlarmName']])
                    print(f"Skipped disabling heartbeat alarm: {alarm['AlarmName']}")
        else:
            print(f"Alarm not found for instance id: {instance_id}")

# Example usage
# handle_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check)


# Example usage
# handle_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check)

# Example usage
# handle_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check)

# Example usage
# handle_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check)


# # Stop instance - disable all alarms except heartbeat alarm
# def handle_stop_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check):
#     # Define a mapping of country codes to time zones
#     country_to_timezone = {
#         'mex': 'America/Mexico_City',
#         'chile': 'America/Santiago',
#         'my': 'Asia/Kuala_Lumpur',
#         'th': 'Asia/Bangkok'
#     }
#
#     # Get the tags
#     tags = instance_info.get('Tags', [])
#
#     # Check for the specified tag key
#     tag_value = next((tag['Value'] for tag in tags if tag['Key'] == tag_key_to_check), None)
#
#     if not tag_value:
#         print('Disabling all alarms as Tag is not present:', tag_key_to_check)
#         handle_tag_change(instance_id, cloudwatch_client)
#         return
#
#     # Extract country, start time, and end time from the tag value
#     parts = tag_value.split('-')
#     if len(parts) < 6:
#         print("Tag value format is incorrect. Expected format: ...-country-environment-start-end")
#         return
#
#     print(f"Parts: {parts}")
#     country_code = parts[2]  # 'mex'
#     start_time_str = parts[4]  # '0820'
#     end_time_str = parts[5]  # '1840'
#
#     # Convert times to hours and minutes
#     start_hour = int(start_time_str[:2])
#     start_minute = int(start_time_str[2:])
#     end_hour = int(end_time_str[:2])
#     end_minute = int(end_time_str[2:])
#
#     # Get the current time for the country's timezone
#     if country_code in country_to_timezone:
#         current_time = datetime.now(pytz.timezone(country_to_timezone[country_code.lower()]))
#         current_hour = current_time.hour
#         current_minute = current_time.minute
#
#         # Check if current time is within the specified range
#         is_within_range = (
#                 (start_hour < current_hour or (start_hour == current_hour and start_minute <= current_minute)) and
#                 (current_hour < end_hour or (current_hour == end_hour and current_minute < end_minute))
#         )
#
#         print(f"Current time: {current_time.strftime('%H:%M')}, Is within range: {is_within_range}")
#
#         # Manage alarms based on time range
#         metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
#         for alarm in metric_alarms['MetricAlarms']:
#             if instance_id in alarm['AlarmName']:
#                 for metrics in alarm['Metrics']:
#                     metric_service_name = metrics['MetricStat']['Metric']['MetricName']
#                     if is_within_range:
#                         if 'ec2_heartbeat_service' not in metric_service_name:
#                             cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
#                             print(f"Disabled alarm action for alarm: {alarm['AlarmName']}")
#                         else:
#                             cloudwatch_client.enable_alarm_actions(AlarmNames=[alarm['AlarmName']])
#                             print(f"Heartbeat Alarm found for instance id: {instance_id}")
#                     else:
#                         # If not in range, disable the alarm
#                         cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
#                         print(f"Disabled alarm action for alarm as current time is NOT in range: {alarm['AlarmName']}")
#             else:
#                 print(f"Alarm not found for instance id: {instance_id}")
#     else:
#         print(f"Country code '{country_code}' not found in the timezone mapping.")
#         handle_tag_change(instance_id, cloudwatch_client)

# # -*- coding: utf-8 -*-
# import boto3
# import json
# from datetime import datetime
# import pytz


# # tag change - enabled,supressed
# def handle_tag_change(instance_id, cloudwatch_client):
#     metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
#     for alarm in metric_alarms['MetricAlarms']:
#         if instance_id in alarm['AlarmName']:
#             cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
#             print(f"Disabled alarm action for alarm : {alarm['AlarmName']}")
#         else:
#             print(f"Alarm not found for instance id : {instance_id}")


# # stop instance - disable all alarms except heartbeat alarm
# def handle_stop_instance(instance_id, cloudwatch_client, instance_info, tag_key_to_check):
#     # Define a mapping of country codes to time zones
#     country_to_timezone = {
#         'mex': 'America/Mexico_City',
#         'ind': 'Asia/Kolkata',
#     }

#     # Get the tags
#     tags = instance_info.get('Tags', [])

#     # Check for the specified tag key
#     tag_value = None
#     for tag in tags:
#         if tag['Key'] == tag_key_to_check:
#             tag_value = tag['Value']
#             break

#     # If the tag is present, process its value
#     if tag_value:
#         # Extract country, start time, and end time from the tag value
#         parts = tag_value.split('-')
#         print(f"Parts: {parts}")
#         country_code = parts[2]  # 'mex'
#         start_time_str = parts[4]  # '0820'
#         end_time_str = parts[5]    # '1840'

#         # Convert times to hours and minutes
#         start_hour = int(start_time_str[:2])  # First two digits for hours
#         start_minute = int(start_time_str[2:])  # Last two digits for minutes
#         end_hour = int(end_time_str[:2])      # First two digits for hours
#         end_minute = int(end_time_str[2:])    # Last two digits for minutes

#         # Get the current time for the country's timezone
#         if country_code in country_to_timezone:
#             current_time = datetime.now(pytz.timezone(country_to_timezone[country_code.lower()]))
#             current_hour = current_time.hour
#             current_minute = current_time.minute

#             # Check if current time is within the specified range
#             is_within_range = (
#                 (start_hour < current_hour or (start_hour == current_hour and start_minute <= current_minute)) and
#                 (current_hour < end_hour or (current_hour == end_hour and current_minute < end_minute))
#             )


#             if is_within_range:
#                 # Print the result
#                 print(f"Current time: {current_time.strftime('%H:%M')}, Is within range: {is_within_range}")
#                 metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
#                 for alarm in metric_alarms['MetricAlarms']:
#                     if instance_id in alarm['AlarmName']:
#                         for metrics in alarm['Metrics']:
#                             metric_service_name = metrics['MetricStat']['Metric']['MetricName']
#                             if 'ec2_heartbeat_service' not in metric_service_name:
#                                 cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
#                                 print(f"Disabled alarm action for alarm : {alarm['AlarmName']}")
#                             else:
#                                 cloudwatch_client.enable_alarm_actions(AlarmNames=[alarm['AlarmName']])
#                                 print(f"Heartbeat Alarm found for instance id : {instance_id}")
#                     else:
#                         print(f"Alarm not found for instance id : {instance_id}")
#             else:
#                 print(f"Current time: {current_time.strftime('%H:%M')}, Is NOT within range: {is_within_range}")
#                 handle_tag_change(instance_id, cloudwatch_client)

#                 # metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
#                 # for alarm in metric_alarms['MetricAlarms']:
#                 #     if instance_id in alarm['AlarmName']:
#                 #         cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
#                 #         print(f"Disabled alarm action for alarm : {alarm['AlarmName']}")
#                 #     else:
#                 #         print(f"Alarm not found for instance id : {instance_id}")

#         else:
#             print(f"Country code '{country_code}' not found in the timezone mapping.")
#     else:
#         print('Disabling all alarms as Tag is not present: ', tag_key_to_check)
#         handle_tag_change(instance_id, cloudwatch_client)

# #         metric_alarms = cloudwatch_client.describe_alarms(AlarmTypes=['MetricAlarm'], AlarmNamePrefix=instance_id)
# #         for alarm in metric_alarms['MetricAlarms']:
# #             if instance_id in alarm['AlarmName']:
# #                 cloudwatch_client.disable_alarm_actions(AlarmNames=[alarm['AlarmName']])
# #                 print(f"Disabled alarm action for alarm : {alarm['AlarmName']}")
# #             else:
# #                 print(f"Alarm not found for instance id : {instance_id}")
