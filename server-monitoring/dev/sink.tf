resource "aws_iam_service_linked_role" "pfg-iaas-server-cloudwatch-service-sink-role" {
  depends_on       = [aws_oam_sink.pfg-iaas-server-monitor-account-oam-sink]
  aws_service_name = "cloudwatch-crossaccount.amazonaws.com"
}

resource "aws_oam_sink" "pfg-iaas-server-monitor-account-oam-sink" {
  name = "pfg-iaas-server-cw-monitor-sink-${data.aws_region.pfg_monitoring_account_region.name}"
}

resource "aws_oam_sink_policy" "pfg-iaas-server-monitor-account-oam-sink-policy" {
  sink_identifier = aws_oam_sink.pfg-iaas-server-monitor-account-oam-sink.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["oam:CreateLink", "oam:UpdateLink"]
        Effect   = "Allow"
        Resource = "*"
        Principal = {
          "AWS" = var.source_account_ids
        }
        Condition = {
          "ForAllValues:StringEquals" = {
            "oam:ResourceTypes" = ["AWS::CloudWatch::Metric", "AWS::Logs::LogGroup"]
          }
        }
      }
    ]
  })
}
