# Centralized cloudwatch monitoring setup for Dev Env

<br>Lets understand modules:</br>

Modules:</br>
    1.    sink -  This module creates sink and sink policy in monitoring account for specific region. This will       enable  the monitoring in cloudwatch settings.
    2.    sink_service_role - This module help us to create sink service role for monitor account, which will enable   cross-account cross-region for all regions
    3.    cw_dashboard - This module creates lambda role and function. This function runs on schedule basis i.e. every 15 mins. This function fetches ec2 instance which are filtered by tags, create metric and composite alarms. Also, this module creates cloudwatch dahboard, which display region and metric specific metrics, alarms and composite alarms.

Metric.json: </br>
     Inside cw_dashboard module, we have folder lambda which has metric.json.This file has all the metrics and their configurations. In case needing to add new metric, add the block of metric with all the configurations.

Outputs:</br>
    In output file, we are getting sink arn values
