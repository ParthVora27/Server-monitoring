resource "aws_cloudwatch_log_group" "pfg_cw_alarms_log_group" {
  name              = "/aws/events/pfg-iaas-server/cw/alarms"
  retention_in_days = 7
  tags = {
    Environment = "/pfg-iaas-server/cw/alarms"
  }
}

resource "aws_cloudwatch_log_metric_filter" "pfg_alarm_history_state_alarm" {
  log_group_name = aws_cloudwatch_log_group.pfg_cw_alarms_log_group.name
  name           = "pfg-iaas-server-alarm-history-state-alarm"
  pattern        = "{$.detail.alarmName=* && $.detail.state.value=\"ALARM\"}"
  metric_transformation {
    name      = "state"
    namespace = "CWAlarms"
    value     = "1"
    dimensions = {
      alarmName = "$.detail.alarmName"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "pfg_alarm_history_state_ok" {
  log_group_name = aws_cloudwatch_log_group.pfg_cw_alarms_log_group.name
  name           = "pfg-iaas-server-alarm-history-state-ok"
  pattern        = "{$.detail.alarmName=* && $.detail.state.value=\"OK\"}"
  metric_transformation {
    name      = "state"
    namespace = "CWAlarms"
    value     = "0"
    dimensions = {
      alarmName = "$.detail.alarmName"
    }
  }
}

resource "aws_cloudwatch_event_rule" "pfg_alarm_history" {
  name = "pfg-iaas-server-alarm-history"
  event_pattern = jsonencode({
    source      = ["aws.cloudwatch"],
    detail-type = ["CloudWatch Alarm State Change"]
  })
}

resource "aws_cloudwatch_event_target" "log_group_target" {
  rule      = aws_cloudwatch_event_rule.pfg_alarm_history.name
  target_id = "send_to_log_group"
  arn       = aws_cloudwatch_log_group.pfg_cw_alarms_log_group.arn
}
