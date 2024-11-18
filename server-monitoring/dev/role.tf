####----- EC2 ON OFF BOARDING LAMBDA IAM -----#####

resource "aws_iam_role" "pfg_monitoring_ec2_on_offboarding_lambda_function_role" {
  name = "pfg-iaas-server-monitoring-ec2-on-off-boarding-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "01"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_policy" "pfg_monitoring_ec2_on_offboarding_lambda_function_policy" {
  name        = "pfg-iaas-server-monitoring-ec2-on-offboarding-lambda-function-policy"
  description = "Policy for lambda to access cloudwatch logs"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_monitoring_ec2_on_offboarding_lambda_function_policy_attachment" {
  role       = aws_iam_role.pfg_monitoring_ec2_on_offboarding_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_monitoring_ec2_on_offboarding_lambda_function_policy.arn
}

resource "aws_iam_policy" "pfg_monitoring_ec2_on_offboarding_lambda_function_dynamodb_policy" {
  name        = "pfg-iaas-server-monitoring-ec2-on-offboarding-lambda-dynamodb-read-put-delete-items-policy"
  description = "Policy for lambda to READ, PUT, DELETE Items in DynamoDB"
  policy = jsonencode({
    "Statement" : [
      {
        "Action" : [
          "dynamodb:DescribeImport",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeContributorInsights",
          "dynamodb:ListTagsOfResource",
          "dynamodb:PartiQLSelect",
          "dynamodb:DescribeTable",
          "dynamodb:GetItem",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:DescribeExport",
          "dynamodb:GetResourcePolicy",
          "dynamodb:DescribeKinesisStreamingDestination",
          "dynamodb:BatchGetItem",
          "dynamodb:ConditionCheckItem",
          "dynamodb:PutItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:DescribeStream",
          "dynamodb:UpdateItem",
          "dynamodb:DescribeTimeToLive",
          "dynamodb:DescribeGlobalTableSettings",
          "dynamodb:GetShardIterator",
          "dynamodb:DescribeGlobalTable",
          "dynamodb:DescribeBackup",
          "dynamodb:GetRecords",
          "dynamodb:DescribeTableReplicaAutoScaling"
        ],
        "Effect" : "Allow",
        "Resource" : "*",
        "Sid" : "VisualEditor0"
      },
      {
        "Action" : [
          "dynamodb:ListContributorInsights",
          "dynamodb:DescribeReservedCapacityOfferings",
          "dynamodb:ListGlobalTables",
          "dynamodb:ListTables",
          "dynamodb:DescribeReservedCapacity",
          "dynamodb:ListBackups",
          "dynamodb:ListImports",
          "dynamodb:DescribeLimits",
          "dynamodb:DescribeEndpoints",
          "dynamodb:ListExports",
          "dynamodb:ListStreams"
        ],
        "Effect" : "Allow",
        "Resource" : "*",
        "Sid" : "VisualEditor1"
      }
    ],
    "Version" : "2012-10-17"
  })
}

resource "aws_iam_role_policy_attachment" "pfg_monitoring_ec2_on_offboarding_lambda_function_dynamodb_policy_attachment" {
  role       = aws_iam_role.pfg_monitoring_ec2_on_offboarding_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_monitoring_ec2_on_offboarding_lambda_function_dynamodb_policy.arn
}

resource "aws_iam_policy" "pfg_monitoring_ec2_on_offboarding_lambda_function_cloudwatch_policy" {
  name        = "pfg-iaas-server-monitoring-ec2-on-offboarding-lambda-function-cloudwatch-policy"
  description = "Policy for lambda to Put Metric Data in cloudwatch"
  policy = jsonencode({
    "Statement" : [
      {
        "Action" : "cloudwatch:PutMetricData",
        "Effect" : "Allow",
        "Resource" : "*",
        "Sid" : "VisualEditor0"
      }
    ],
    "Version" : "2012-10-17"
  })
}

resource "aws_iam_role_policy_attachment" "pfg_monitoring_ec2_on_offboarding_lambda_function_cloudwatch_policy_attachment" {
  role       = aws_iam_role.pfg_monitoring_ec2_on_offboarding_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_monitoring_ec2_on_offboarding_lambda_function_cloudwatch_policy.arn
}

resource "aws_iam_policy" "pfg_monitoring_ec2_on_offboarding_lambda_function_cross_account_policy" {
  name        = "pfg-iaas-server-monitoring-ec2-on-offboarding-lambda-function-cross-account-policy"
  description = "Policy for lambda to work with cross account role"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : "sts:AssumeRole",
        "Resource" : "arn:aws:iam::*:role/pfg-iaas-server-cw-dashboard-cross-account-role"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_monitoring_ec2_on_offboarding_lambda_function_cross_account_policy_attachment" {
  role       = aws_iam_role.pfg_monitoring_ec2_on_offboarding_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_monitoring_ec2_on_offboarding_lambda_function_cross_account_policy.arn
}

####----- RESOURCE GENERATOR LAMBDA IAM -----#####

resource "aws_iam_role" "pfg_resource_generator_lambda_function_role" {
  name = "pfg-iaas-server-resource-generator-lambda-function-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "01"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_policy" "pfg_resource_generator_lambda_function_policy" {
  name        = "pfg-iaas-server-resource-generator-lambda-function-policy"
  description = "Policy for lambda to access cloudwatch logs"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_resource_generator_lambda_function_policy_attachment" {
  role       = aws_iam_role.pfg_resource_generator_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_resource_generator_lambda_function_policy.arn
}

resource "aws_iam_policy" "pfg_resource_generator_lambda_function_cloudwatch_policy" {
  name        = "pfg-iaas-server-resource-generator-lambda-function-cloudwatch-policy"
  description = "Policy for lambda to work with cloudwatch alarms"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:PutDashboard",
          "cloudwatch:GetDashboard",
          "cloudwatch:EnableAlarmActions",
          "cloudwatch:DeleteAlarms",
          "cloudwatch:GetMetricData",
          "cloudwatch:DisableAlarmActions",
          "cloudwatch:DescribeAlarmsForMetric",
          "cloudwatch:ListDashboards",
          "cloudwatch:DescribeAlarms",
          "cloudwatch:PutCompositeAlarm",
          "cloudwatch:ListMetrics"
        ],
        "Resource" : "*"
      }
    ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "pfg_resource_generator_lambda_function_cloudwatch_policy_attachment" {
  role       = aws_iam_role.pfg_resource_generator_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_resource_generator_lambda_function_cloudwatch_policy.arn
}

resource "aws_iam_policy" "pfg_resource_generator_lambda_function_dynamodb_stream_policy" {
  name        = "pfg-iaas-server-resource-generator-lambda-function-dynamodb-stream-policy"
  description = "Policy for lambda to work with dynamodb streams"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:GetShardIterator",
          "dynamodb:DescribeStream",
          "dynamodb:ListStreams",
          "dynamodb:GetRecords"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_resource_generator_lambda_function_dynamodb_stream_policy_attachment" {
  role       = aws_iam_role.pfg_resource_generator_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_resource_generator_lambda_function_dynamodb_stream_policy.arn
}

resource "aws_iam_policy" "pfg_resource_generator_lambda_function_cross_account_policy" {
  name        = "pfg-iaas-server-resource-generator-lambda-function-cross-account-policy"
  description = "Policy for lambda to work with cross account role"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : "sts:AssumeRole",
        "Resource" : "arn:aws:iam::*:role/pfg-iaas-server-cw-dashboard-cross-account-role"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_resource_generator_lambda_function_cross_account_policy_attachment" {
  role       = aws_iam_role.pfg_resource_generator_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_resource_generator_lambda_function_cross_account_policy.arn
}

resource "aws_iam_role_policy_attachment" "pfg_resource_generator_lambda_function_ec2_read_only_policy_attachment" {
  role       = aws_iam_role.pfg_resource_generator_lambda_function_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "pfg_resource_generator_lambda_function_s3_read_only_policy_attachment" {
  role       = aws_iam_role.pfg_resource_generator_lambda_function_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "pfg_resource_generator_lambda_function_sqs_policy_attachment" {
  role       = aws_iam_role.pfg_resource_generator_lambda_function_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

####----- ALARM LAMBDA IAM -----#####

resource "aws_iam_role" "pfg_cw_alarm_report_lambda_function_role" {
  name = "pfg-iaas-server-cw-alarm-report-lambda-function-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "pfg_cw_alarm_report_lambda_function_policy" {
  name        = "pfg-iaas-server-cw-alarm-report-lambda-function-policy"
  description = "Policy for lambda to work with cloudwatch logs, s3 bucket"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "logs:CreateLogGroup",
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : [
          "*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:PutObject",
          "s3:GetObject"
        ],
        "Resource" : [
          aws_s3_bucket.pfg_cw_reports_s3_bucket.arn,
          "${aws_s3_bucket.pfg_cw_reports_s3_bucket.arn}/*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:GetQueryResults",
          "logs:StartQuery"
        ],
        "Resource" : [
          "${aws_cloudwatch_log_group.pfg_cw_alarms_log_group.arn}:*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_cw_alarm_report_lambda_function_policy_attachment" {
  role       = aws_iam_role.pfg_cw_alarm_report_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_cw_alarm_report_lambda_function_policy.arn
}

#####----- METRIC SQS LAMBDA IAM -----#####

resource "aws_iam_role" "pfg_cw_metric_sqs_event_lambda_function_role" {
  name = "pfg-iaas-server-cw-metric-sqs-event-lambda-function-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "pfg_cw_metric_sqs_event_lambda_function_policy" {
  name        = "pfg-iaas-server-cw-metric-sqs-event-lambda-function-policy"
  description = "Policy for lambda to work with cloudwatch logs, sqs, parameter store"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "logs:CreateLogGroup",
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : [
          "*"
        ]
      },
      {
        "Sid" : "Statement1",
        "Effect" : "Allow",
        "Action" : [
          "sqs:SendMessage"
        ],
        "Resource" : [
          aws_sqs_queue.pfg_sqs.arn,
          #"arn:aws:sqs:us-west-2:009160073618:pfg-iaas-server-cw-reports-sqs",
          #"arn:aws:sqs:us-west-2:009160073618:pfg-iaas-server-sqs"
        ]
      },
      {
        "Sid" : "Statement2",
        "Effect" : "Allow",
        "Action" : [
          "ssm:GetParameters"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_cw_metric_sqs_event_lambda_function_policy_attachment" {
  role       = aws_iam_role.pfg_cw_metric_sqs_event_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_cw_metric_sqs_event_lambda_function_policy.arn
}

#####----- METRIC REPORT LAMBDA IAM -----######

resource "aws_iam_role" "pfg_cw_metric_report_generator_lambda_function_role" {
  name = "pfg-iaas-server-cw-metric-report-generator-lambda-function-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "pfg_cw_metric_report_generator_lambda_function_policy" {
  name        = "pfg-iaas-server-cw-metric-report-generator-lambda-function-policy"
  description = "Policy for lambda to work with cloudwatch logs, sqs, parameter store"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "logs:CreateLogGroup",
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : [
          "*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:PutObject",
          "s3:GetObject"
        ],
        "Resource" : [
          aws_s3_bucket.pfg_cw_reports_s3_bucket.arn,
          "${aws_s3_bucket.pfg_cw_reports_s3_bucket.arn}/*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ],
        "Resource" : [
          aws_sqs_queue.pfg_sqs.arn,
          #"arn:aws:sqs:us-west-2:009160073618:pfg-iaas-server-cw-reports-sqs",
          #"arn:aws:sqs:us-west-2:009160073618:pfg-iaas-server-sqs"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "cloudwatch:ListMetrics",
          "cloudwatch:GetMetricData"
        ],
        "Resource" : "*"
      }
    ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "pfg_cw_metric_report_generator_lambda_function_policy_attachment" {
  role       = aws_iam_role.pfg_cw_metric_report_generator_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_cw_metric_report_generator_lambda_function_policy.arn
}

#####----- CUSTOM WIDGET EC2 MONITORING & ALARM LAMBDA IAM -----######

resource "aws_iam_role" "pfg_custom_widget_lambda_function_role" {
  name = "pfg-iaas-server-custom-widget-lambda-function-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "pfg_custom_widget_lambda_function_policy" {
  name        = "pfg-iaas-server-custom-widget-lambda-function-policy"
  description = "Policy for lambda to work with cloudwatch custom widget"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "*"
      },
      {
        "Action" : [
          "sts:AssumeRole",
          "cloudwatch:GetDashboard",
          "cloudwatch:PutDashboard",
          "cloudwatch:ListDashboards",
          "cloudwatch:ListMetrics",
          "cloudwatch:GetMetricData",
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:DeleteAlarms",
          "cloudwatch:EnableAlarmActions",
          "cloudwatch:DisableAlarmActions",
          "cloudwatch:DescribeAlarms",
          "cloudwatch:PutCompositeAlarm",
          "cloudwatch:DescribeAlarmsForMetric"
        ],
        "Effect" : "Allow",
        "Resource" : "*"
      }
    ]
    }
  )
}

resource "aws_iam_role_policy_attachment" "pfg_custom_widget_lambda_function_policy_attachment" {
  role       = aws_iam_role.pfg_custom_widget_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_custom_widget_lambda_function_policy.arn
}

resource "aws_iam_role_policy_attachment" "pfg_custom_widget_lambda_function_db_read_only_policy_attachment" {
  role       = aws_iam_role.pfg_custom_widget_lambda_function_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
}

####----- DRIFT MANAGEMENT LAMBDA IAM -----#####

resource "aws_iam_role" "pfg_drift_management_lambda_function_role" {
  name = "pfg-iaas-server-drift-management-lambda-function-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "01"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_policy" "pfg_drift_management_lambda_function_policy" {
  name        = "pfg-iaas-server-drift-management-lambda-function-policy"
  description = "Policy for lambda to access cloudwatch logs"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pfg_drift_management_lambda_function_policy_attachment" {
  role       = aws_iam_role.pfg_drift_management_lambda_function_role.name
  policy_arn = aws_iam_policy.pfg_drift_management_lambda_function_policy.arn
}

resource "aws_iam_role_policy_attachment" "pfg_drift_management_lambda_function_dynamodb_policy_attachment" {
  role       = aws_iam_role.pfg_drift_management_lambda_function_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}
