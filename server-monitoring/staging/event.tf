# Create custom event bus
resource "aws_cloudwatch_event_bus" "pfg_iaas_server_custom_event_bus" {
  name = "pfg-iaas-server-custom-event-bus"
}

# # Enable schema discovery for custom event bus
# resource "null_resource" "pfg_initiate_schema_discovery" {
#   provisioner "local-exec" {
#     command = "aws schemas create-discoverer --source-arn ${aws_cloudwatch_event_bus.pfg_iaas_server_custom_event_bus.arn} --region ${data.aws_region.pfg_monitoring_account_region.name}"
#   }
#   depends_on = [aws_cloudwatch_event_bus.pfg_iaas_server_custom_event_bus]
# }

# Create event bus policy
data "aws_iam_policy_document" "pfg_iaas_server_bus_policy" {
  statement {
    sid    = "01"
    effect = "Allow"
    actions = [
      "events:PutEvents",
    ]
    resources = [
      aws_cloudwatch_event_bus.pfg_iaas_server_custom_event_bus.arn
    ]

    principals {
      type        = "AWS"
      identifiers = var.source_account_ids
    }
  }
}

# Create permission policy for custom event bus
resource "aws_cloudwatch_event_bus_policy" "pfg_iaas_server_permission_policy" {
  event_bus_name = aws_cloudwatch_event_bus.pfg_iaas_server_custom_event_bus.name
  policy         = data.aws_iam_policy_document.pfg_iaas_server_bus_policy.json
}

# ----------------------- On ec2 state change ----------------------------
# Create rule on ec2 state change
resource "aws_cloudwatch_event_rule" "pfg_iaas_server_ec2_state_change_rule" {
  name           = "pfg-iaas-server-ec2-state-change-rule"
  description    = "Trigger lambda function on ec2 instance state change"
  event_bus_name = aws_cloudwatch_event_bus.pfg_iaas_server_custom_event_bus.name
  event_pattern = jsonencode({
    "source" : ["aws.ec2"],
    "detail-type" : ["EC2 Instance State-change Notification"],
    "detail" : {
      "state" : ["running", "terminated", "stopped"]
    }
  })
}

# creating target as lambda
resource "aws_cloudwatch_event_target" "pfg_iaas_server_ec2_state_change_lambda_target" {
  rule           = aws_cloudwatch_event_rule.pfg_iaas_server_ec2_state_change_rule.name
  target_id      = "lambdaTarget"
  arn            = aws_lambda_function.pfg_monitoring_ec2_on_offboarding_lambda_function.arn
  event_bus_name = aws_cloudwatch_event_bus.pfg_iaas_server_custom_event_bus.name
}

# ----------------------- On ec2 tag value change (pfg-iaas-server-monitoring)----------------------------
# Create rule on tag change monitor
resource "aws_cloudwatch_event_rule" "pfg_iaas_server_monitor_tag_value_alarm_rule" {
  name           = "pfg-iaas-server-ec2-tag-change-rule"
  description    = "Trigger lambda function on ec2 tag value change"
  event_bus_name = aws_cloudwatch_event_bus.pfg_iaas_server_custom_event_bus.name
  event_pattern = jsonencode({
    "source" : ["aws.tag"],
    "detail-type" : ["Tag Change on Resource"],
    "detail" : {
      "service" : ["ec2"],
      "changed-tag-keys" : ["pfg-server-monitoring"]
    }
  })
}

# creating target as lambda
resource "aws_cloudwatch_event_target" "pfg_iaas_server_tag_value_lambda_target" {
  rule           = aws_cloudwatch_event_rule.pfg_iaas_server_monitor_tag_value_alarm_rule.name
  target_id      = "lambdaTarget"
  arn            = aws_lambda_function.pfg_monitoring_ec2_on_offboarding_lambda_function.arn
  event_bus_name = aws_cloudwatch_event_bus.pfg_iaas_server_custom_event_bus.name
}
