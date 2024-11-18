# -*- coding: utf-8 -*-
import json
import boto3
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from metric_data import get_metric_info

# value form environ
s3_bucket_name = os.environ["s3_bucket_name"]
custom_metric_name = os.environ["custom_metric_name"]


def lambda_handler(event, context):
    print(f"Event: {event}")
    print(context.invoked_function_arn)

    # Basic settings and data handling
    widget_context = event.get("widgetContext", {})
    form_data = widget_context.get("forms", {}).get("all", {})

    instance_id = str(form_data.get('instanceId', '') or '')
    account_id = str(form_data.get('accountId', '') or '')
    region = str(form_data.get('region', '') or '')

    # checking input
    print(f"instnace id: {instance_id}")
    print(f"account id: {account_id}")
    print(f"region: {region}")

    # Check if the report has been generated
    report_generated = False

    customWidget = event.get('widgetContext', {})
    form_data = customWidget.get("forms", {}).get("all", {})
    print(f"form_data: {form_data}")
    if customWidget:
        endTime = event.get('widgetContext', {}).get('timeRange', {}).get('end', '')
        startTime = event.get('widgetContext', {}).get('timeRange', {}).get('start', '')
        endTime_dt = datetime.fromtimestamp(int(endTime) / 1000)
        endDateTime = endTime_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        startTime_dt = datetime.fromtimestamp(int(startTime) / 1000)
        startDateTime = startTime_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        period = event.get('widgetContext', {}).get('period', '')
        region = form_data.get('region', '')
        instance_id = form_data.get('instanceId', '')
        account_id = form_data.get('accountId', '')
        frequency = 'ondemand'
        body = {
            "accountId": account_id,
            "endDateTime": endDateTime,
            "period": period,
            "startDateTime": startDateTime,
            "frequency": frequency,
            "region": region,
            "instanceId": instance_id
        }

    print('body ', body)

    region = body.get('region')
    accountId = body.get('accountId')
    instanceId = body.get('instance_id')
    period = body.get('period', {})
    startTime = body.get('startDateTime', {})
    endTime = body.get('endDateTime', {})
    frequency = body.get('frequency', {})

    final_list = []
    platformList = ['linux', 'windows']

    if not form_data:
        return f""" <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        h2{{ margin-bottom: 20px;}}
                        .input-group {{
                            margin-bottom: 20px;
                        }}
                        .container {{
                            text-align: center;
                            padding: 20px;
                            max-width: 400px;
                            margin: 0 auto;
                            border: 2px solid #000000;
                            border-radius: 5px;
                            background-color: #f9f9f9;
                        }}
                        .input-group {{
                            margin-bottom: 20px;
                            display: flex;
                            border: #000000;
                            justify-content: space-between;
                            align-items: center;
                        }}
                        .input-group label {{
                            flex: 1;
                            margin-right: 10px;
                            font-weight: bold;
                            border: 1px solid #d1d5a;
                            border-radius: 3px;
                            text-align: left;
                        }}
                        .input-group input {{
                            flex: 2;
                            padding: 5px;
                            border: 1px solid #d1d5a;
                            border-radius: 3px;
                            width: 100%;
                        }}
                        .btn {{
                            padding: 7px 15px;
                            background-color: #0073bb;
                            color: #fff;
                            border: 1px solid #000000;
                            cursor: pointer;
                            border-radius: 3px;
                            text-align: center;
                            display: inline-block;
                            margin-top: 10px;
                            transition: background-color 0.3s ease, border-color 0.3s ease;
                        }}
                        .btn:hover {{
                            background-color: #005f99;
                            border-color: #005f99;
                        }}
                        #infoMessage {{
                            color: red;
                            font-size: 12px;
                            margin-bottom: 10px;
                        }}
                        .download-link {{
                            margin-top: 20px;
                            display: inline-block;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Generate Metric Report</h2>
                        <br>
                         <form id="form1" style="text-align: center;">
                              <div class="input-group" style="justify-content: center;">

                                <label for="region">Region:</label>
                                    <select id="region" name="region" style="flex:2; padding:5px; border: 1px solid #d1d5a; border-radius: 3px; width:100%; text-align: left; text-align-last: left;" onchange="validateForm()">
                                        <option value="">Select Region</option>
                                        <option value="us-east-1" {"selected" if region == "us-east-1" else ""}>us-east-1</option>
                                        <option value="us-west-2" {"selected" if region == "us-west-2" else ""}>us-west-2</option>
                                    </select>
                              </div>
                            <div class="input-group" style="justify-content: center;">
                                <label for="accountId">Account ID:</label>
                                <input type="text" id="accountId" name="accountId" value="{account_id}"/>
                            </div>
                            <div class="input-group" style="justify-content: center;">
                                <label for="instanceId">Instance ID:</label>
                                <input type="text" id="instanceId" name="instanceId" value="{instance_id}" />
                            </div>
                            <a class="btn btn-primary">Generate Report</a>
                                <cwdb-action action="call" endpoint="{context.invoked_function_arn}"></cwdb-action>
                        </form>
                    </div>

                    </div>
                </body>
                </html>
                """
    else:
        if not accountId or not region:
            return f"""
                     <html>
                        <head>
                            <style>
                                .popup-container {{
                                    position: fixed;
                                    top: 50%;
                                    left: 50%;
                                    transform: translate(-50%, -50%);
                                    padding: 30px;
                                    background-color: #f9f9f9;
                                    border: 2px solid black;
                                    border-radius: 10px;
                                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                                    z-index: 1000;
                                    text-align: center;
                                    width: 400px;
                                }}

                                .popup-container h3 {{
                                    margin-bottom: 20px;
                                    font-size: 18px;
                                    color: #333;
                                }}

                                .btn {{
                                    padding: 10px 20px;
                                    background-color: #0073bb;
                                    color: #fff;
                                    border: none;
                                    cursor: pointer;
                                    border-radius: 5px;
                                    margin-top: 10px;
                                    text-decoration: none;
                                    display: inline-block;
                                }}

                                .btn:hover {{
                                    background-color: #005f99;
                                }}

                                .overlay {{
                                    position: fixed;
                                    top: 0;
                                    left: 0;
                                    width: 100%;
                                    height: 100%;
                                    background-color:#f9f9f9;
                                    display: block;
                                    z-index: 999;
                                }}
                                .close-btn {{
                                    margin-top: 10px;
                                    padding: 5px 15px;
                                    background-color: #f44336;
                                    color: white;
                                    border: none;
                                    cursor: pointer;
                                    border-radius: 3px;
                                }}

                                .close-btn:hover {{
                                    background-color: #d32f2f;
                                }}
                            </style>
                         </head>
                    <body>
                        <!-- Dark overlay -->
                        <div id="overlay" class="overlay"></div>
                        <!-- Pop-up container -->
                        <div id="popup" class="popup-container">
                            <h3>Warning!!</h3>
                            <p> AccountId and Region required </p>
                            <br><br>
                            <cwdb-action action="close">
                                <button class="close-btn" onclick="document.getElementById('popup').style.display='none'; document.getElementById('overlay').style.display='none';">Close</button>
                            </cwdb-action>
                        </div>
                    </body>
                </html>
            """
        if not instanceId:
            print("andar")
            for platform in platformList:
                instance_list = get_ec2_instances(accountId, platform, region)
                print('instance_list ', instance_list)
                for instanceId in instance_list:
                    response = get_metric_info(accountId, period, instanceId, platform, startTime, endTime, region)
                    response_list = response['MetricDataResults']
                    print('response_list ', response_list)
                    timestamp_list = response_list[0]['Timestamps']
                    metrics_list = []
                    for metric in response_list:
                        for i in range(len(timestamp_list) - len(metric['Timestamps'])):
                            metric['Timestamps'].append(0)
                            metric['Values'].append(0)

                        metric_list = []
                        for j in range(len(timestamp_list)):
                            if (metric['Timestamps'][j] == timestamp_list[j]):
                                metric_list.append(round((metric['Values'][j]), 2))
                            else:
                                metric_list.append(0)
                        metrics_list.append(metric_list)

                    perInstance_list = []
                    for ts in timestamp_list:
                        perInstance_list.append([ts.strftime("%Y-%m-%d %H:%M:%S"), instanceId, platform])

                    for ts_val in range(len(timestamp_list)):
                        for ms_val in range(len(metrics_list)):
                            perInstance_list[ts_val].append(metrics_list[ms_val][ts_val])
                    print('perInstance_list ', perInstance_list)

                    final_list.extend(perInstance_list)
        else:
            for platform in platformList:
                response = get_metric_info(accountId, period, instance_id, platform, startTime, endTime, region)
                response_list = response['MetricDataResults']
                print('response_list ', response_list)
                timestamp_list = response_list[0]['Timestamps']
                print("timestamp", timestamp_list)
                metrics_list = []
                for metric in response_list:
                    for i in range(len(timestamp_list) - len(metric['Timestamps'])):
                        metric['Timestamps'].append(0)
                        metric['Values'].append(0)

                    metric_list = []
                    for j in range(len(timestamp_list)):
                        if (metric['Timestamps'][j] == timestamp_list[j]):
                            metric_list.append(round((metric['Values'][j]), 2))
                        else:
                            metric_list.append(0)
                    metrics_list.append(metric_list)
                    print(metric_list)

                perInstance_list = []
                for ts in timestamp_list:
                    perInstance_list.append([ts.strftime("%Y-%m-%d %H:%M:%S"), instance_id, platform])

                for ts_val in range(len(timestamp_list)):
                    for ms_val in range(len(metrics_list)):
                        perInstance_list[ts_val].append(metrics_list[ms_val][ts_val])
                print('perInstance_list ', perInstance_list)

                final_list.extend(perInstance_list)

        print('finalList', final_list)
        presigned_url = create_excel(accountId, final_list, region, frequency)
        print(presigned_url)

        # Showing download report button on the basis of flag
        if presigned_url:
            report_generated = True
            download_report_link = f'<a href="{presigned_url}" class="btn btn-primary" download>Download Metric Report</a>'

        # HTML content with updated styling
        return f"""
                     <html>
                        <head>
                            <style>
                                .popup-container {{
                                    position: fixed;
                                    top: 50%;
                                    left: 50%;
                                    transform: translate(-50%, -50%);
                                    padding: 30px;
                                    background-color: #f9f9f9;
                                    border: 2px solid black;
                                    border-radius: 10px;
                                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                                    z-index: 1000;
                                    text-align: center;
                                    width: 400px;
                                }}

                                .popup-container h3 {{
                                    margin-bottom: 20px;
                                    font-size: 18px;
                                    color: #333;
                                }}

                                .btn {{
                                    padding: 10px 20px;
                                    background-color: #0073bb;
                                    color: #fff;
                                    border: none;
                                    cursor: pointer;
                                    border-radius: 5px;
                                    margin-top: 10px;
                                    text-decoration: none;
                                    display: inline-block;
                                }}

                                .btn:hover {{
                                    background-color: #005f99;
                                }}

                                .overlay {{
                                    position: fixed;
                                    top: 0;
                                    left: 0;
                                    width: 100%;
                                    height: 100%;
                                    background-color:#f9f9f9;
                                    display: block;
                                    z-index: 999;
                                }}
                                .close-btn {{
                                    margin-top: 10px;
                                    padding: 5px 15px;
                                    background-color: #f44336;
                                    color: white;
                                    border: none;
                                    cursor: pointer;
                                    border-radius: 3px;
                                }}

                                .close-btn:hover {{
                                    background-color: #d32f2f;
                                }}
                            </style>
                         </head>
                    <body>
                        <!-- Dark overlay -->
                        <div id="overlay" class="overlay"></div>
                        <!-- Pop-up container -->
                        <div id="popup" class="popup-container">
                            <h3>Metric report is ready!</h3>
                            <a href="{presigned_url}" class="btn btn-primary" download>Download Metric Report</a>
                            <br><br>
                            <cwdb-action action="close">
                                <button class="close-btn" onclick="document.getElementById('popup').style.display='none'; document.getElementById('overlay').style.display='none';">Close</button>
                            </cwdb-action>
                        </div>
                    </body>
                </html>
            """


def create_excel(accountId, final_list, region, frequency):
    try:
        if not final_list:
            print("No data to write to Excel.")
            return None

        df = pd.DataFrame(final_list,
                          columns=['TimeStamp', 'InstanceId', 'Platform',
                                   'CPUUtilization(Percent)', 'NetworkIn(Bytes)',
                                   'NetworkOut(Bytes)', 'Paging(Bytes)',
                                   'Memory(Percent)', 'Disk(Percent)',
                                   'DiskIORead(Bytes)', 'DiskIOWrite(Bytes)'])

        currdate = datetime.now()
        file_name = f"{currdate}.csv"
        file_path = f"/tmp/{file_name}"

        df.to_csv(file_path, index=False)
        print(f"CSV file created at {file_path}")

        s3_client = boto3.client("s3")
        s3_key = f'Metrics/{accountId}/{region}/{frequency}/{file_name}'

        with open(file_path, "rb") as file:
            s3_client.upload_fileobj(file, s3_bucket_name, s3_key, ExtraArgs={'ACL': 'bucket-owner-full-control'})
            print(f"Uploaded to S3: {s3_key}")

        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': s3_bucket_name, 'Key': s3_key},
                                                    ExpiresIn=3600)
        return response

    except Exception as e:
        print(f"Error while trying to push to s3: {str(e)}")


def get_ec2_instances(accountId, platform, region):
    try:
        client = boto3.client('cloudwatch', region_name=region)
        if platform == 'linux':
            metric_name = 'mem_used_percent'
        else:
            metric_name = 'Memory % Committed Bytes In Use'

        response = client.list_metrics(
            Namespace=custom_metric_name,
            MetricName=metric_name,
            Dimensions=[
                {
                    'Name': 'InstanceId'
                },
            ],
            IncludeLinkedAccounts=True,
            OwningAccount=accountId
        )

        instanceList = []
        metrics = response.get('Metrics', {})
        if (metrics):
            for metric in metrics:
                dimensions = metric.get('Dimensions', {})
                if (dimensions):
                    for dimension in dimensions:
                        if dimension['Name'] == 'InstanceId':
                            if (dimension['Value'] not in instanceList):
                                instanceList.append(dimension['Value'])
        # print('instanceList', instanceList)
        return instanceList
    except Exception as e:
        print(f"Error retrieving EC2 for account {accountId} :{str(e)}")

# import boto3
# import json
# import os
# import pandas as pd
# from datetime import datetime, timedelta

# from metric_data import get_metric_info

# s3_bucket_name = os.environ["s3_bucket_name"]
# custom_metric_name = os.environ["custom_metric_name"]


# def lambda_handler(event, context):
#     print('event', event)

#     try:
#         records = event.get('Records', {})
#         for record in records:
#             body = json.loads(record.get('body', {}))

#         customWidget = event.get('widgetContext', {})
#         if customWidget:
#             endTime = event.get('widgetContext', {}).get('timeRange', {}).get('end', '')
#             startTime = event.get('widgetContext', {}).get('timeRange', {}).get('start', '')
#             endTime_dt = datetime.fromtimestamp(int(endTime) / 1000)
#             endDateTime = endTime_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
#             startTime_dt = datetime.fromtimestamp(int(startTime) / 1000)
#             startDateTime = startTime_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
#             period = event.get('widgetContext', {}).get('period', '')
#             accountId = event['accountId']
#             region = event['region']
#             print("Line 41: {}".format(accountId))
#             frequency = 'ondemand'
#             body = {
#                 "accountId": accountId,
#                 "endDateTime": endDateTime,
#                 "period": period,
#                 "startDateTime": startDateTime,
#                 "frequency": frequency,
#                 "region": region
#             }

#         print('body ', body)

#         accountId = body.get('accountId')

#         period = body.get('period', {})
#         startTime = body.get('startDateTime', {})
#         endTime = body.get('endDateTime', {})
#         frequency = body.get('frequency', {})

#         final_list = []
#         platformList = ['linux', 'windows']
#         for platform in platformList:
#             instance_list = get_ec2_instances(accountId, platform)
#             # instance_list = ["i-0880fe87c428471d6"]
#             print('instance_list ', instance_list)
#             for instanceId in instance_list:
#                 response = get_metric_info(accountId, period, instanceId, platform, startTime, endTime)
#                 response_list = response['MetricDataResults']
#                 print('response_list ', response_list)
#                 timestamp_list = response_list[0]['Timestamps']
#                 metrics_list = []
#                 for metric in response_list:
#                     for i in range(len(timestamp_list) - len(metric['Timestamps'])):
#                         metric['Timestamps'].append(0)
#                         metric['Values'].append(0)

#                     metric_list = []
#                     for j in range(len(timestamp_list)):
#                         if (metric['Timestamps'][j] == timestamp_list[j]):
#                             metric_list.append(round((metric['Values'][j]), 2))
#                         else:
#                             metric_list.append(0)
#                     metrics_list.append(metric_list)

#                 perInstance_list = []
#                 for ts in timestamp_list:
#                     perInstance_list.append([ts.strftime("%Y-%m-%d %H:%M:%S"), instanceId, platform])

#                 for ts_val in range(len(timestamp_list)):
#                     for ms_val in range(len(metrics_list)):
#                         perInstance_list[ts_val].append(metrics_list[ms_val][ts_val])
#                 print('perInstance_list ', perInstance_list)

#                 final_list.extend(perInstance_list)
#         print('finalList', final_list)
#         presigned_url = create_excel(accountId, final_list, region, frequency)
#         print(presigned_url)

#         # with open('/var/task/index.html', 'r') as file:
#         #     html_content = file.read()
#         #     html_content = html_content.replace('{{accountId}}', accountId if accountId else '')
#         #     html_content = html_content.replace('{{region}}', region if region else '')
#         # if presigned_url:
#         #     html_content = html_content.replace('{{presigned_url}}', presigned_url if presigned_url else '')
#         # else:

#         #     html_content = html_content.replace('{{presigned_url}}', '')

#         # return f'{html_content}'
#         return "<a class=\"btn btn-primary\" href ={}>Download Report</a>".format(presigned_url)
#         #return f"<html><body> <div><a class=\"btn btn-primary\">Download Your Report</a><cwdb-action action=\"call\" confirmation=\"message\" display=\"popup\" endpoint=\"arn:aws:lambda:us-west-2:350104896611:function:custom-widget-lambda\" event=\"click\"> <a href=\"https://www.google.com\" }}\">Download</a> </cwdb-action> </div> </body> </html>"

#     except Exception as e:
#         print(f"Error while fetching metrics:{str(e)}")

#     # return html_content


# def create_excel(accountId, final_list, region, frequency):
#     try:
#         if not final_list:
#             print("No data to write to Excel.")
#             return None

#         df = pd.DataFrame(final_list,
#                           columns=['TimeStamp', 'InstanceId', 'Platform',
#                                   'CPUUtilization(Percent)', 'NetworkIn(Bytes)',
#                                   'NetworkOut(Bytes)', 'Paging(Bytes)',
#                                   'Memory(Percent)', 'Disk(Percent)',
#                                   'DiskIORead(Bytes)', 'DiskIOWrite(Bytes)'])

#         currdate = datetime.now()
#         file_name = f"{currdate}.csv"
#         file_path = f"/tmp/{file_name}"

#         df.to_csv(file_path, index=False)
#         print(f"CSV file created at {file_path}")

#         s3_client = boto3.client("s3")
#         s3_key = f'Metrics/{accountId}/{region}/{frequency}/{file_name}'

#         with open(file_path, "rb") as file:
#             s3_client.upload_fileobj(file, s3_bucket_name, s3_key, ExtraArgs={'ACL': 'bucket-owner-full-control'})
#             print(f"Uploaded to S3: {s3_key}")

#         response = s3_client.generate_presigned_url('get_object',
#                                                       Params={'Bucket': s3_bucket_name, 'Key': s3_key},
#                                                       ExpiresIn=3600)
#         return response

#     except Exception as e:
#         print(f"Error while trying to push to s3: {str(e)}")


# def get_ec2_instances(accountId, platform):
#     try:
#         client = boto3.client('cloudwatch')
#         if platform == 'linux':
#             metric_name = 'mem_used_percent'
#         else:
#             metric_name = 'Memory % Committed Bytes In Use'

#         response = client.list_metrics(
#             Namespace=custom_metric_name,
#             MetricName=metric_name,
#             Dimensions=[
#                 {
#                     'Name': 'InstanceId'
#                 },
#             ],
#             IncludeLinkedAccounts=True,
#             OwningAccount=accountId
#         )

#         instanceList = []
#         metrics = response.get('Metrics', {})
#         if (metrics):
#             for metric in metrics:
#                 dimensions = metric.get('Dimensions', {})
#                 if (dimensions):
#                     for dimension in dimensions:
#                         if dimension['Name'] == 'InstanceId':
#                             if (dimension['Value'] not in instanceList):
#                                 instanceList.append(dimension['Value'])
#         # print('instanceList', instanceList)
#         return instanceList
#     except Exception as e:
#         print(f"Error retrieving EC2 for account {accountId} :{str(e)}")
