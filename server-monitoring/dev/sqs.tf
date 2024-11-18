resource "aws_sqs_queue" "pfg_sqs" {
  name                       = "pfg-iaas-server-cw-reports-sqs"
  visibility_timeout_seconds = 600
  tags = {
    Name = "pfg-iaas-server-cw-reports-sqs"
  }
}

resource "aws_sqs_queue_policy" "sqs_policy" {
  queue_url = aws_sqs_queue.pfg_sqs.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Id" : "__default_policy_ID",
    "Statement" : [
      {
        "Sid" : "__owner_statement",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:aws:iam::${data.aws_caller_identity.pfg_monitoring_account.account_id}:root"
        },
        "Action" : "SQS:*",
        "Resource" : aws_sqs_queue.pfg_sqs.arn
      }
    ]
  })
}

#### RESOURCE GENERATOR LAMBDA - INSERT OPERATION ####
resource "aws_sqs_queue" "pfg_sqs_alarm_creation" {
  name                       = "pfg-iaas-server-alarm-creation-sqs"
  visibility_timeout_seconds = 900
  delay_seconds              = 900
  tags = {
    Name = "pfg-iaas-server-alarm-creation-sqs"
  }
}

resource "aws_sqs_queue_policy" "pfg_sqs_alarm_creation_policy" {
  queue_url = aws_sqs_queue.pfg_sqs_alarm_creation.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Id" : "__default_policy_ID",
    "Statement" : [
      {
        "Sid" : "__owner_statement",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:aws:iam::${data.aws_caller_identity.pfg_monitoring_account.account_id}:root"
        },
        "Action" : "SQS:*",
        "Resource" : aws_sqs_queue.pfg_sqs_alarm_creation.arn
      }
    ]
  })
}
