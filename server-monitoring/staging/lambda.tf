#####--------- EC2 ON OFF BOARDING LAMBDA FUNCTION ----------#####

data "archive_file" "pfg_ec2_onoffboarding_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-functions/pfg-iaas-server-monitoring-ec2-on-offboarding-lambda"
  output_path = "${path.module}/lambda-functions/pfg-iaas-server-monitoring-ec2-on-offboarding-lambda.zip"
}

resource "aws_lambda_function" "pfg_monitoring_ec2_on_offboarding_lambda_function" {
  filename         = data.archive_file.pfg_ec2_onoffboarding_lambda_zip.output_path
  function_name    = "pfg-iaas-server-monitoring-ec2-on-offboarding-lambda"
  role             = aws_iam_role.pfg_monitoring_ec2_on_offboarding_lambda_function_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pfg_ec2_onoffboarding_lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 600
  environment {
    variables = {
      dynamodb_table_name          = aws_dynamodb_table.pfg_ec2_monitoring_dynamodb_table.name
      dynamodb_table_partition_key = aws_dynamodb_table.pfg_ec2_monitoring_dynamodb_table.hash_key
      dynamodb_table_sort_key      = aws_dynamodb_table.pfg_ec2_monitoring_dynamodb_table.range_key
      # dynamodb_table_region      = [for attr in aws_dynamodb_table.ec2_monitoring_dynamodb_table.attribute : attr if attr.name == "Region"][0]
    }
  }
}

resource "aws_lambda_permission" "pfg_allow_eventbridge_ec2_state_change" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pfg_monitoring_ec2_on_offboarding_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.pfg_iaas_server_ec2_state_change_rule.arn
}

resource "aws_lambda_permission" "pfg_allow_eventbridge_ec2_tag_change" {
  statement_id  = "AllowExecutionFromEventBridgeForEC2TagChange"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pfg_monitoring_ec2_on_offboarding_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.pfg_iaas_server_monitor_tag_value_alarm_rule.arn
}

#####--------- RESOURCE GENERATOR LAMBDA FUNCTION ----------#####

resource "aws_lambda_layer_version" "pfg_resource_generator_lambda_layer" {
  layer_name = "pytz_layer"
  filename   = "${path.module}/lambda-functions/pytz_layer.zip"
}

data "archive_file" "pfg_resource_generator_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-functions/pfg-iaas-server-resource-generator-lambda"
  output_path = "${path.module}/lambda-functions/pfg-iaas-server-resource-generator-lambda.zip"
}

resource "aws_lambda_function" "pfg_resource_generator_lambda_function" {
  filename         = data.archive_file.pfg_resource_generator_lambda_zip.output_path
  function_name    = "pfg-iaas-server-resource-generator-lambda"
  role             = aws_iam_role.pfg_resource_generator_lambda_function_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pfg_resource_generator_lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 600
  layers           = [aws_lambda_layer_version.pfg_resource_generator_lambda_layer.arn]
  environment {
    variables = {
      monitoring_account      = data.aws_caller_identity.pfg_monitoring_account.account_id
      sns_topic_create_ticket = data.aws_sns_topic.pfg_sns_alarm_create_ticket.arn
      sns_topic_close_ticket  = data.aws_sns_topic.pfg_sns_alarm_close_ticket.arn
      dashboard_name          = "GLOBAL_DASHBOARD"
      account_dashboard_name  = "ACCOUNTS_DASHBOARD"
      pfg_instance_schedule   = "pfg-instance-schedule"
      bucket_name             = aws_s3_bucket.pfg_drift_management_s3_bucket.bucket
      sqs_url_alarm_creation  = aws_sqs_queue.pfg_sqs_alarm_creation.url
    }
  }
}

resource "aws_lambda_event_source_mapping" "pfg_alarm_creation_sqs_trigger" {
  event_source_arn = aws_sqs_queue.pfg_sqs_alarm_creation.arn
  function_name    = aws_lambda_function.pfg_resource_generator_lambda_function.arn
  enabled          = true
}

#####--------- ALARM REPORT LAMBDA FUNCTION ----------#####

data "archive_file" "pfg_cw_alarm_report_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-functions/pfg-iaas-server-cw-alarm-report-lambda"
  output_path = "${path.module}/lambda-functions/pfg-iaas-server-cw-alarm-report-lambda.zip"
}

#### Alarm state change -> eventbridge triggered ->
#### eventbridge target -> cloudwatch log group
#### lambda reads data from this log group and sends report to s3
resource "aws_lambda_function" "pfg_cw_alarm_report_lambda_function" {
  filename         = data.archive_file.pfg_cw_alarm_report_lambda_zip.output_path
  function_name    = "pfg-iaas-server-cw-alarm-report-lambda"
  role             = aws_iam_role.pfg_cw_alarm_report_lambda_function_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pfg_cw_alarm_report_lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 600
  layers = [
    "arn:aws:lambda:${data.aws_region.pfg_monitoring_account_region.name}:336392948345:layer:AWSSDKPandas-Python39:25"

  ]
  environment {
    variables = {
      logGroupName   = aws_cloudwatch_log_group.pfg_cw_alarms_log_group.name
      query          = "fields @timestamp, detail.alarmName as alarmName, detail.state.value as alarmState, @message | filter alarmName not like 'Composite'| filter alarmState not like 'INSUFFICIENT_DATA' | sort @timestamp desc"
      s3_bucket_name = aws_s3_bucket.pfg_cw_reports_s3_bucket.bucket
    }
  }
}

#####--------- METRIC REPORT LAMBDA FUNCTION ----------#####

#### EVENT SCHEDULER TRIGGER LAMBDA

data "archive_file" "pfg_cw_metric_sqs_event_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-functions/pfg-iaas-server-cw-metric-sqs-event-lambda"
  output_path = "${path.module}/lambda-functions/pfg-iaas-server-cw-metric-sqs-event-lambda.zip"
}

resource "aws_lambda_function" "pfg_cw_metric_sqs_event_lambda_function" {
  filename         = data.archive_file.pfg_cw_metric_sqs_event_lambda_zip.output_path
  function_name    = "pfg-iaas-server-cw-metric-sqs-event-lambda"
  role             = aws_iam_role.pfg_cw_metric_sqs_event_lambda_function_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pfg_cw_metric_sqs_event_lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 600
  environment {
    variables = {
      parameter_store_name = aws_ssm_parameter.pfg_source_account_list.name
      sqs_url              = aws_sqs_queue.pfg_sqs.url
    }
  }
}

##### SQS TRIGGER METRIC REPORT LAMBDA

data "archive_file" "pfg_cw_metric_report_generator_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-functions/pfg-iaas-server-cw-metric-report-generator-lambda"
  output_path = "${path.module}/lambda-functions/pfg-iaas-server-cw-metric-report-generator-lambda.zip"
}

resource "aws_lambda_function" "pfg_cw_report_generator_lambda_function" {
  filename         = data.archive_file.pfg_cw_metric_report_generator_lambda_zip.output_path
  function_name    = "pfg-iaas-server-cw-metric-report-generator-lambda"
  role             = aws_iam_role.pfg_cw_metric_report_generator_lambda_function_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pfg_cw_metric_report_generator_lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 600
  layers = [
    "arn:aws:lambda:${data.aws_region.pfg_monitoring_account_region.name}:336392948345:layer:AWSSDKPandas-Python39:25"
  ]
  environment {
    variables = {
      s3_bucket_name = aws_s3_bucket.pfg_cw_reports_s3_bucket.bucket
      #TODO Modify metric name value
      custom_metric_name = "CWAgent"
    }
  }
}

resource "aws_lambda_event_source_mapping" "pfg_sqs_trigger" {
  event_source_arn = aws_sqs_queue.pfg_sqs.arn
  function_name    = aws_lambda_function.pfg_cw_report_generator_lambda_function.arn
  enabled          = true
}

##### CUSTOM WIDGET EC2 MONITORING LAMBDA

data "archive_file" "pfg_custom_widget_ec2_monitoring_summary_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-functions/pfg-iaas-server-custom-widget-ec2-monitoring-summary-lambda"
  output_path = "${path.module}/lambda-functions/pfg-iaas-server-custom-widget-ec2-monitoring-summary-lambda.zip"
}

resource "aws_lambda_function" "pfg_custom_widget_ec2_monitoring_summary_lambda_function" {
  filename         = data.archive_file.pfg_custom_widget_ec2_monitoring_summary_lambda_zip.output_path
  function_name    = "pfg-iaas-server-custom-widget-ec2-monitoring-summary-lambda"
  role             = aws_iam_role.pfg_custom_widget_lambda_function_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pfg_custom_widget_ec2_monitoring_summary_lambda_zip.output_base64sha256
  runtime          = "python3.12"
  timeout          = 600
  environment {
    variables = {
      dynamodb_table_name = aws_dynamodb_table.pfg_ec2_monitoring_dynamodb_table.name
    }
  }
}

##### CUSTOM WIDGET ALARM LAMBDA

data "archive_file" "pfg_custom_widget_alarm_summary_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-functions/pfg-iaas-server-custom-widget-alarm-summary-lambda"
  output_path = "${path.module}/lambda-functions/pfg-iaas-server-custom-widget-alarm-summary-lambda.zip"
}

resource "aws_lambda_function" "pfg_custom_widget_alarm_summary_lambda_function" {
  filename         = data.archive_file.pfg_custom_widget_alarm_summary_lambda_zip.output_path
  function_name    = "pfg-iaas-server-custom-widget-alarm-summary-lambda"
  role             = aws_iam_role.pfg_custom_widget_lambda_function_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pfg_custom_widget_alarm_summary_lambda_zip.output_base64sha256
  runtime          = "python3.12"
  timeout          = 600
}

#####--------- DRIFT MANAGEMENT LAMBDA FUNCTION ----------#####
data "archive_file" "pfg_drift_management_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda-functions/pfg-iaas-server-drift-management-lambda"
  output_path = "${path.module}/lambda-functions/pfg-iaas-server-drift-management-lambda.zip"
}

resource "aws_lambda_function" "pfg_drift_management_lambda_function" {
  filename         = data.archive_file.pfg_drift_management_lambda_zip.output_path
  function_name    = "pfg-iaas-server-drift-management-lambda"
  role             = aws_iam_role.pfg_drift_management_lambda_function_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.pfg_drift_management_lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 600
  environment {
    variables = {
      dynamodb_table_name          = aws_dynamodb_table.pfg_ec2_monitoring_dynamodb_table.name
      dynamodb_table_partition_key = aws_dynamodb_table.pfg_ec2_monitoring_dynamodb_table.hash_key
      dynamodb_table_sort_key      = aws_dynamodb_table.pfg_ec2_monitoring_dynamodb_table.range_key
    }
  }
}

resource "aws_lambda_permission" "pfg_drift_management_lambda_permission" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pfg_drift_management_lambda_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.pfg_drift_management_s3_bucket.arn
  depends_on    = [aws_s3_bucket.pfg_drift_management_s3_bucket]
}

resource "aws_s3_bucket_notification" "pfg_drift_management_lambda_trigger" {
  bucket = aws_s3_bucket.pfg_drift_management_s3_bucket.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.pfg_drift_management_lambda_function.arn
    events              = ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
  }
  depends_on = [aws_lambda_permission.pfg_drift_management_lambda_permission]
}
