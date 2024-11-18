# -*- coding: utf-8 -*-
import boto3
import json
import os

from datetime import datetime, timedelta

parameter_store_name = os.environ["parameter_store_name"]
sqs_url = os.environ["sqs_url"]


def lambda_handler(event, context):
    try:
        frequency = event.get('frequency', {})
        startDateTime = ''
        endDateTime = ''
        period = ''
        if (frequency == 'daily'):
            endDateTime = datetime.now().strftime("%Y-%m-%d 00:00:00.000000")
            startDateTime = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00.000000")
            period = 3600
        elif (frequency == 'weekly'):
            endDateTime = datetime.now().strftime("%Y-%m-%d 00:00:00.000000")
            startDateTime = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00.000000")
            period = 86400
        '''else:
            frequency = 'ondemand'
            print('ondemand')
            endTime = event.get('widgetContext',{}).get('timeRange',{}).get('end','')
            startTime = event.get('widgetContext',{}).get('timeRange',{}).get('start','')
            endTime_dt = datetime.fromtimestamp(int(endTime)/1000)
            endDateTime = endTime_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
            startTime_dt = datetime.fromtimestamp(int(startTime)/1000)
            startDateTime = startTime_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
            period = event.get('widgetContext',{}).get('period','')
            accountId = event.get('widgetContext',{}).get('accountId','')'''
        # endDateTime = event.get('endDateTime',{}) + '.000000'
        # startDateTime = event.get('startDateTime',{}) + '.000000'

        # accountList = ["891377252169", "290769750486"]
        ssmclient = boto3.client('ssm')
        getresponse = ssmclient.get_parameters(Names=[parameter_store_name])
        parameters = getresponse.get('Parameters', {})
        parameter_value = parameters[0].get('Value', {})
        accountList = parameter_value.split(",")
        # print('accountList', accountList)

        sqs = boto3.client('sqs')
        QueueUrl = sqs_url

        if frequency == 'daily' or frequency == 'weekly':
            for accountId in accountList:
                body = {
                    "accountId": accountId,
                    "endDateTime": endDateTime,
                    "period": period,
                    "startDateTime": startDateTime,
                    "frequency": frequency
                }
                print('daily ', body)
                sqs.send_message(
                    QueueUrl=QueueUrl,
                    MessageBody=json.dumps(body)
                )

            '''elif frequency=='ondemand':
                body = {
                        "accountId": accountId,
                        "endDateTime": endDateTime,
                        "period": period,
                        "startDateTime": startDateTime,
                        "frequency": frequency
                    }
                print('body', body)
                sqs.send_message(
                    QueueUrl =  QueueUrl,
                    MessageBody = json.dumps(body)
                )'''
        else:
            return {
                'statusCode': 200,
                'body': json.dumps('Frequency invalid')
            }

        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }

    except Exception as e:
        # print(f"Something went wrong, Please Investigate :{str(e)}")
        return {
            'StatusCode': 400,
            'Message': 'Something went wrong, Please Investigate. Error --> ' + str(e)
        }
