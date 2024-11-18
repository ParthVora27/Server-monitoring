resource "aws_cloudwatch_dashboard" "pfg_cw_custom_admin_dashboard" {
  dashboard_name = "ADMIN_DASHBOARD"
  dashboard_body = file("cw-dashboard/admin_dashboard.json")
}

resource "aws_cloudwatch_dashboard" "pfg_cw_custom_reporting_dashboard" {
  dashboard_name = "REPORTING_DASHBOARD"
  dashboard_body = templatefile("cw-dashboard/reporting_dashboard.json", {
    pfg-iaas-server-cw-metric-report-generator-lambda = aws_lambda_function.pfg_cw_report_generator_lambda_function.arn,
    pfg-iaas-server-cw-alarm-report-lambda            = aws_lambda_function.pfg_cw_alarm_report_lambda_function.arn
  })
}
