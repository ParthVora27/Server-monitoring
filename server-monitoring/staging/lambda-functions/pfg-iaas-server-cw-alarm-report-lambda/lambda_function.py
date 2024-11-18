# -*- coding: utf-8 -*-
import json
import boto3
import datetime
import json
import os
import pandas as pd
import time
from datetime import datetime, timedelta


def lambda_handler(event, context):
    print(f"Event: {event}")

    # Basic settings and data handling
    widget_context = event.get("widgetContext", {})
    form_data = widget_context.get("forms", {}).get("all", {})
    account_id = str(form_data.get('accountId', '') or '')
    region = str(form_data.get('region', '') or os.environ['AWS_REGION'])

    print(f"account id: {account_id}")
    print(f"region: {region}")

    # Check if the report has been generated
    report_generated = False

    customWidget = event.get('widgetContext', {})
    form_data = customWidget.get("forms", {}).get("all", {})
    logGroupName = os.getenv('logGroupName')
    queryString = os.getenv("query")
    s3_bucket_name = os.getenv("s3_bucket_name")
    frequency = event.get('frequency', {})
    startDateTime = ''
    endDateTime = ''
    accountId = str(form_data.get('accountId', '') or '')
    # region = str(form_data.get('region', '') or '')
    print(f"form_data: {form_data}")

    if customWidget and not form_data:
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
                        <h2>Generate Alarm Report</h2>
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
                            <a class="btn btn-primary">Generate Report</a>
                                <cwdb-action action="call" endpoint="{context.invoked_function_arn}"></cwdb-action>
                        </form>
                    </div>

                    </div>
                </body>
                </html>
                """

    else:
        if not region:
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
                            <p> Region is required </p>
                            <br><br>
                            <cwdb-action action="close">
                                <button class="close-btn" onclick="document.getElementById('popup').style.display='none'; document.getElementById('overlay').style.display='none';">Close</button>
                            </cwdb-action>
                        </div>
                    </body>
                </html>
            """
        try:

            if (frequency == 'daily'):
                endDateTime = datetime.now().strftime("%Y-%m-%d 00:00:00.000000")
                startDateTime = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00.000000")

            elif (frequency == 'weekly'):
                endDateTime = datetime.now().strftime("%Y-%m-%d 00:00:00.000000")
                startDateTime = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00.000000")

            else:
                frequency = 'ondemand'
                endTime = event.get('widgetContext', {}).get('timeRange', {}).get('end', '')
                startTime = event.get('widgetContext', {}).get('timeRange', {}).get('start', '')
                endDateTime = datetime.fromtimestamp(int(endTime) / 1000)
                startDateTime = datetime.fromtimestamp(int(startTime) / 1000)

            # startDateTime = os.getenv('startDateTime')
            getStartMilsec = convertToMil(str(startDateTime))
            print('getStartMilsec', getStartMilsec)

            # endDateTime = os.getenv('endDateTime')
            getEndMilsec = convertToMil(str(endDateTime))
            print('getEndMilsec', getEndMilsec)

            response_list_data = []
            list_data = get_query_response(logGroupName, getStartMilsec, getEndMilsec, queryString, response_list_data,
                                           region)

            print('list_data ', list_data)

            final_list = []
            for data in list_data:
                child_list = []
                for dataval in data:
                    if (dataval['field'] == '@timestamp'):
                        child_list.append(dataval['value'])
                    if (dataval['field'] == 'alarmName'):
                        child_list.append(dataval['value'])
                    if (dataval['field'] == 'alarmState'):
                        child_list.append(dataval['value'])
                    if (dataval['field'] == '@message'):
                        message = json.loads(dataval['value'])
                        accountId = ''
                        instanceId = ''
                        reason = ''
                        metrics = message.get('detail', {}).get('configuration', {}).get('metrics')
                        if (metrics):
                            metric = metrics[0]
                            instanceId = metric.get('metricStat', {}).get('metric', {}).get('dimensions').get(
                                'InstanceId')
                            if (instanceId):
                                instanceId = instanceId
                            accountId = metric.get('accountId', {})
                            if (accountId):
                                accountId = accountId

                        reason = message.get('detail', {}).get('state', {}).get('reason')
                        if (reason):
                            reason = reason

                        child_list.append(accountId)
                        child_list.append(instanceId)
                        child_list.append(reason)
                        child_list.append(dataval['value'])
                final_list.append(child_list)

                # print('final_list ', final_list)
            df = pd.DataFrame(final_list,
                              columns=['TimeStamp', 'AlarmName', 'Status', 'AccountId', 'InstanceId', 'Reason',
                                       'Message'])

            currdate = datetime.now()
            file_name = f"{currdate}.csv"
            file_path = f"/tmp/{file_name}"

            df.to_csv(file_path, index=False)

            s3_client = boto3.client("s3", region_name=region)

            with open(file_path, "rb") as file:
                s3_client.upload_fileobj(file, s3_bucket_name, f'Alarms/{region}/{frequency}/{file_name}')

            presigned_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': s3_bucket_name,
                                                                                   'Key': f'Alarms/{region}/{frequency}/{file_name}'},
                                                             ExpiresIn=3600)

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
                                <h3>Alarm report is ready!</h3>
                                <a href="{presigned_url}" class="btn btn-primary" download>Download Alarm Report</a>
                                <br><br>
                                <cwdb-action action="close">
                                    <button class="close-btn" onclick="document.getElementById('popup').style.display='none'; document.getElementById('overlay').style.display='none';">Close</button>
                                </cwdb-action>
                            </div>
                        </body>
                    </html>
                """

        except Exception as e:
            print("Something went wrong, please investigate")


def get_query_response(logGroupName, getStartMilsec, getEndMilsec, queryString, response_list_data, region):
    print("Inside query data")
    client = boto3.client('logs', region_name=region)
    try:
        start_query_response = client.start_query(
            logGroupName=logGroupName,
            startTime=getStartMilsec,
            endTime=getEndMilsec,
            queryString=queryString
        )
        print(start_query_response)
    except Exception as e:
        print(f"No log streams present")

    query_id = start_query_response['queryId']
    print('query_id', query_id)
    queryResponse = None

    while queryResponse == None or queryResponse['status'] == 'Running':
        time.sleep(1)
        queryResponse = client.get_query_results(queryId=query_id)

    # print('queryResponse ', queryResponse)

    response_list_data.extend(queryResponse["results"])
    print('length ', len(queryResponse["results"]))
    recordsLength = len(queryResponse["results"])

    if recordsLength > 9999:
        querylength = len(queryResponse["results"])
        getEndMilsec = convertToMil(queryResponse["results"][querylength - 1][0]['value'])
        get_query_response(logGroupName, getStartMilsec, getEndMilsec, queryString, response_list_data)

    return response_list_data


def convertToMil(value):
    dt_obj = datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S.%f')
    result = int(dt_obj.timestamp())
    return result

# import boto3
# import datetime
# import json
# import os
# import pandas as pd
# import time
# from datetime import datetime, timedelta


# def lambda_handler(event, context):
#     print(event)
#     try:
#         logGroupName = os.getenv('logGroupName')
#         print(logGroupName)
#         queryString = os.getenv("query")
#         s3_bucket_name = os.getenv("s3_bucket_name")
#         frequency = event.get('frequency', {})
#         startDateTime = ''
#         endDateTime = ''
#         accountId = event['accountId']
#         region = event['region']
#         if (frequency == 'daily'):
#             endDateTime = datetime.now().strftime("%Y-%m-%d 00:00:00.000000")
#             startDateTime = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00.000000")
#             # print('startDateTime', startDateTime)
#             # print('endDateTime', endDateTime)
#         elif (frequency == 'weekly'):
#             endDateTime = datetime.now().strftime("%Y-%m-%d 00:00:00.000000")
#             startDateTime = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00.000000")
#             # print('startDateTime', startDateTime)
#             # print('endDateTime', endDateTime)
#         else:
#             frequency = 'ondemand'
#             endTime = event.get('widgetContext', {}).get('timeRange', {}).get('end', '')
#             startTime = event.get('widgetContext', {}).get('timeRange', {}).get('start', '')
#             endDateTime = datetime.fromtimestamp(int(endTime) / 1000)
#             startDateTime = datetime.fromtimestamp(int(startTime) / 1000)
#             # print('startDateTime', startDateTime)
#             # print('endDateTime', endDateTime)

#         # startDateTime = os.getenv('startDateTime')
#         getStartMilsec = convertToMil(str(startDateTime))
#         print('getStartMilsec', getStartMilsec)

#         # endDateTime = os.getenv('endDateTime')
#         getEndMilsec = convertToMil(str(endDateTime))
#         print('getEndMilsec', getEndMilsec)

#         response_list_data = []
#         list_data = get_query_response(logGroupName, getStartMilsec, getEndMilsec, queryString, response_list_data)

#         print('list_data ', list_data)

#         final_list = []
#         for data in list_data:
#             child_list = []
#             for dataval in data:
#                 if (dataval['field'] == '@timestamp'):
#                     child_list.append(dataval['value'])
#                 if (dataval['field'] == 'alarmName'):
#                     child_list.append(dataval['value'])
#                 if (dataval['field'] == 'alarmState'):
#                     child_list.append(dataval['value'])
#                 if (dataval['field'] == '@message'):
#                     message = json.loads(dataval['value'])
#                     accountId = ''
#                     instanceId = ''
#                     reason = ''
#                     metrics = message.get('detail', {}).get('configuration', {}).get('metrics')
#                     if (metrics):
#                         metric = metrics[0]
#                         instanceId = metric.get('metricStat', {}).get('metric', {}).get('dimensions').get('InstanceId')
#                         if (instanceId):
#                             instanceId = instanceId
#                         accountId = metric.get('accountId', {})
#                         if (accountId):
#                             accountId = accountId

#                     reason = message.get('detail', {}).get('state', {}).get('reason')
#                     if (reason):
#                         reason = reason

#                     child_list.append(accountId)
#                     child_list.append(instanceId)
#                     child_list.append(reason)
#                     child_list.append(dataval['value'])
#             final_list.append(child_list)

#             # print('final_list ', final_list)
#         df = pd.DataFrame(final_list,
#                           columns=['TimeStamp', 'AlarmName', 'Status', 'AccountId', 'InstanceId', 'Reason', 'Message'])

#         currdate = datetime.now()
#         file_name = f"{currdate}.csv"
#         file_path = f"/tmp/{file_name}"

#         df.to_csv(file_path, index=False)

#         s3_client = boto3.client("s3")

#         with open(file_path, "rb") as file:
#             s3_client.upload_fileobj(file, s3_bucket_name, f'Alarms/{region}/{frequency}/{file_name}')

#         presigned_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': s3_bucket_name,
#                                                                               'Key': f'Alarms/{region}/{frequency}/{file_name}'},
#                                                          ExpiresIn=3600)
#         return "<a class=\"btn btn-primary\" href ={}>Download Report</a>".format(presigned_url)

#     except Exception as e:
#         print("Something went wrong, please investigate")

#         return {
#             'StatusCode': 400,
#             'Message': 'Something went wrong, Please Investigate. Error --> ' + str(e)
#         }


# def get_query_response(logGroupName, getStartMilsec, getEndMilsec, queryString, response_list_data):
#     client = boto3.client('logs')
#     start_query_response = client.start_query(
#         logGroupName=logGroupName,
#         startTime=getStartMilsec,
#         endTime=getEndMilsec,
#         queryString=queryString
#     )

#     query_id = start_query_response['queryId']
#     print('query_id', query_id)
#     queryResponse = None

#     while queryResponse == None or queryResponse['status'] == 'Running':
#         time.sleep(1)
#         queryResponse = client.get_query_results(queryId=query_id)

#     # print('queryResponse ', queryResponse)

#     response_list_data.extend(queryResponse["results"])
#     print('length ', len(queryResponse["results"]))
#     recordsLength = len(queryResponse["results"])

#     if recordsLength > 9999:
#         querylength = len(queryResponse["results"])
#         getEndMilsec = convertToMil(queryResponse["results"][querylength - 1][0]['value'])
#         get_query_response(logGroupName, getStartMilsec, getEndMilsec, queryString, response_list_data)

#     return response_list_data


# def convertToMil(value):
#     dt_obj = datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S.%f')
#     result = int(dt_obj.timestamp())
#     return result
