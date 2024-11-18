resource "aws_ssm_parameter" "pfg_source_account_list" {
  name        = "/iaas/server/dashboard/accountList"
  description = "List of accounts for the metrics sqs lambda"
  type        = "StringList"
  value       = var.metric_report_lambda_account_ids
}
