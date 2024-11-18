#############------ SCHEDULER IAM ------#############

resource "aws_iam_role" "pfg_cw_report_scheduler_role" {
  name = "pfg-iaas-server-cw-report-scheduler-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "scheduler.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {
          "StringEquals" : {
            "aws:SourceAccount" : data.aws_caller_identity.pfg_monitoring_account.account_id
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "pfg_cw_report_scheduler_policy" {
  name        = "pfg-iaas-server-cw-report-scheduler-policy"
  description = "Policy for lambda to work with cloudwatch logs, s3 bucket"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Resource" : [
          "${aws_lambda_function.pfg_cw_alarm_report_lambda_function.arn}:*",
          aws_lambda_function.pfg_cw_alarm_report_lambda_function.arn,
          "${aws_lambda_function.pfg_cw_metric_sqs_event_lambda_function.arn}:*",
          aws_lambda_function.pfg_cw_metric_sqs_event_lambda_function.arn,
          "${aws_lambda_function.pfg_drift_management_lambda_function.arn}:*",
          aws_lambda_function.pfg_drift_management_lambda_function.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_scheduler_attachment" {
  role       = aws_iam_role.pfg_cw_report_scheduler_role.name
  policy_arn = aws_iam_policy.pfg_cw_report_scheduler_policy.arn
}

#############------ SCHEDULER GROUP ------#############

resource "aws_scheduler_schedule_group" "pfg_scheduler_group" {
  name = "pfg-iaas-server-report"
}

resource "aws_scheduler_schedule_group" "pfg_drift_management_scheduler_group" {
  name = "pfg-iaas-server-drift-management"
}

#############------ ALARM REPORT SCHEDULER ------#############

resource "aws_scheduler_schedule" "pfg_alarm_report_daily_scheduler" {
  name                         = "pfg-iaas-server-alarm-report-daily"
  schedule_expression          = "cron(00 01 * * ? *)"
  schedule_expression_timezone = "Asia/Kolkata"
  group_name                   = aws_scheduler_schedule_group.pfg_scheduler_group.name
  target {
    arn      = aws_lambda_function.pfg_cw_alarm_report_lambda_function.arn
    role_arn = aws_iam_role.pfg_cw_report_scheduler_role.arn
    input = jsonencode({
      frequency = "daily"
    })
  }
  flexible_time_window {
    mode = "OFF"
  }
}

resource "aws_scheduler_schedule" "pfg_alarm_report_weekly_scheduler" {
  name                         = "pfg-iaas-server-alarm-report-weekly"
  schedule_expression          = "cron(00 01 ? * 1 *)"
  schedule_expression_timezone = "Asia/Kolkata"
  group_name                   = aws_scheduler_schedule_group.pfg_scheduler_group.name
  target {
    arn      = aws_lambda_function.pfg_cw_alarm_report_lambda_function.arn
    role_arn = aws_iam_role.pfg_cw_report_scheduler_role.arn
    input = jsonencode({
      frequency = "weekly"
    })
  }
  flexible_time_window {
    mode = "OFF"
  }
}

#############------ METRIC REPORT SCHEDULER ------#############

resource "aws_scheduler_schedule" "pfg_metric_report_daily_scheduler" {
  name                         = "pfg-iaas-server-metric-report-daily"
  schedule_expression          = "cron(00 01 * * ? *)"
  schedule_expression_timezone = "Asia/Kolkata"
  group_name                   = aws_scheduler_schedule_group.pfg_scheduler_group.name
  target {
    arn      = aws_lambda_function.pfg_cw_metric_sqs_event_lambda_function.arn
    role_arn = aws_iam_role.pfg_cw_report_scheduler_role.arn
    input = jsonencode({
      frequency = "daily"
    })
  }
  flexible_time_window {
    mode = "OFF"
  }
}

resource "aws_scheduler_schedule" "pfg_metric_report_weekly_scheduler" {
  name                         = "pfg-iaas-server-metric-report-weekly"
  schedule_expression          = "cron(00 01 ? * 1 *)"
  schedule_expression_timezone = "Asia/Kolkata"
  group_name                   = aws_scheduler_schedule_group.pfg_scheduler_group.name
  target {
    arn      = aws_lambda_function.pfg_cw_metric_sqs_event_lambda_function.arn
    role_arn = aws_iam_role.pfg_cw_report_scheduler_role.arn
    input = jsonencode({
      frequency = "weekly"
    })
  }
  flexible_time_window {
    mode = "OFF"
  }
}

#############------ DRIFT MANAGEMENT SCHEDULER ------#############

resource "aws_scheduler_schedule" "pfg_drift_management_daily_scheduler" {
  name                         = "pfg-iaas-drift-management-daily-schedule"
  schedule_expression          = "cron(00 07 * * ? *)"
  schedule_expression_timezone = "Asia/Kolkata"
  group_name                   = aws_scheduler_schedule_group.pfg_drift_management_scheduler_group.name
  target {
    arn      = aws_lambda_function.pfg_drift_management_lambda_function.arn
    role_arn = aws_iam_role.pfg_cw_report_scheduler_role.arn
    input = jsonencode({
      frequency = "weekly"
    })
  }
  flexible_time_window {
    mode = "OFF"
  }
}
