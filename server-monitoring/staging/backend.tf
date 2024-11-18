# This table is used by other pipelines managing resrouces in this account
resource "aws_dynamodb_table" "terraform_state_lock" {
  name         = "terraform-state-lock"
  hash_key     = "LockID"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    pfg-data-class      = "internal"
    pfg-privacy-class   = "not-personal-data"
    pfg-data-retention  = "d30"
    pfg-recovery-method = "unnecessary"
  }
}

terraform {
  backend "s3" {
    bucket         = "serverops-artifacts-009160073638-us-east-1"
    key            = "terraform/serverops-management.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
  }
}
