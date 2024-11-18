# report s3 bucket
resource "aws_s3_bucket" "pfg_cw_reports_s3_bucket" {
  bucket = "pfg-iaas-server-cw-report-${data.aws_caller_identity.pfg_monitoring_account.account_id}-${data.aws_region.pfg_monitoring_account_region.name}"
}

# drift management : metrics config s3 bucket
resource "aws_s3_bucket" "pfg_drift_management_s3_bucket" {
  bucket = "pfg-iaas-server-drift-management-config-${data.aws_caller_identity.pfg_monitoring_account.account_id}-${data.aws_region.pfg_monitoring_account_region.name}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pfg_drift_managements_bucket_encryption" {
  bucket = aws_s3_bucket.pfg_drift_management_s3_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "pfg_drift_management_bucket_versioning" {
  bucket = aws_s3_bucket.pfg_drift_management_s3_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_object" "upload_linux_monitoring_config_file" {
  key                    = "linux.json"
  bucket                 = aws_s3_bucket.pfg_drift_management_s3_bucket.id
  source                 = "${path.module}/monitoring-configs/linux.json"
  etag                   = filemd5("${path.module}/monitoring-configs/linux.json")
  server_side_encryption = "aws:kms"
  acl                    = "bucket-owner-full-control"
}

resource "aws_s3_object" "upload_windows_monitoring_config_file" {
  key                    = "windows.json"
  bucket                 = aws_s3_bucket.pfg_drift_management_s3_bucket.id
  source                 = "${path.module}/monitoring-configs/windows.json"
  etag                   = filemd5("${path.module}/monitoring-configs/windows.json")
  server_side_encryption = "aws:kms"
  acl                    = "bucket-owner-full-control"
}
