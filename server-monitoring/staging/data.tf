data "aws_sns_topic" "pfg_sns_alarm_create_ticket" {
  name = "xmatters-use1-staging-XMattersPageCriticalTopic"
}

data "aws_sns_topic" "pfg_sns_alarm_close_ticket" {
  name = "xmatters-use1-staging-XMattersCloseTopic"
}

data "aws_caller_identity" "pfg_monitoring_account" {}

data "aws_region" "pfg_monitoring_account_region" {}
