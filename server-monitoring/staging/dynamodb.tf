#monitoring dynamodb
resource "aws_dynamodb_table" "pfg_ec2_monitoring_dynamodb_table" {
  name                        = "pfg-iaas-server-ec2-monitoring-${data.aws_region.pfg_monitoring_account_region.name}"
  billing_mode                = "PAY_PER_REQUEST"
  deletion_protection_enabled = true

  hash_key  = "Instance_Id"
  range_key = "Account_Id"
  attribute {
    name = "Instance_Id"
    type = "S"
  }
  attribute {
    name = "Account_Id"
    type = "N"
  }
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  tags = {
    Name = "pfg-iaas-server-ec2-monitoring"
  }
}

resource "aws_lambda_event_source_mapping" "pfg_dynamodb_streams_mapping_lambda" {
  event_source_arn  = aws_dynamodb_table.pfg_ec2_monitoring_dynamodb_table.stream_arn
  function_name     = aws_lambda_function.pfg_resource_generator_lambda_function.arn
  starting_position = "LATEST"
  batch_size        = 1
}
