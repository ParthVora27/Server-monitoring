terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.13"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
  required_version = ">=1.0.0"
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      pfg-owner            = "dlistechsvcscrosspla@exchange.principal.com"
      pfg-cost-center      = "h887-000"
      pfg-app-inventory-id = "no-entry"
      pfg-service-id       = "is.foundationalservices"
      pfg-repo-name        = var.repo_name
    }
  }
  ignore_tags {
    key_prefixes = ["foundation:"]
  }
}

provider "aws" {
  alias  = "us-west-2"
  region = "us-west-2"
  default_tags {
    tags = {
      pfg-owner            = "dlistechsvcscrosspla@exchange.principal.com"
      pfg-cost-center      = "h887-000"
      pfg-app-inventory-id = "no-entry"
      pfg-service-id       = "is.foundationalservices"
      pfg-repo-name        = var.repo_name
    }
  }
  ignore_tags {
    key_prefixes = ["foundation:"]
  }
}

provider "aws" {
  alias  = "ap-southeast-1"
  region = "ap-southeast-1"
  default_tags {
    tags = {
      pfg-owner            = "dlistechsvcscrosspla@exchange.principal.com"
      pfg-cost-center      = "h887-000"
      pfg-app-inventory-id = "no-entry"
      pfg-service-id       = "is.foundationalservices"
      pfg-repo-name        = var.repo_name
    }
  }
  ignore_tags {
    key_prefixes = ["foundation:"]
  }
}

provider "aws" {
  alias  = "ap-southeast-2"
  region = "ap-southeast-2"
  default_tags {
    tags = {
      pfg-owner            = "dlistechsvcscrosspla@exchange.principal.com"
      pfg-cost-center      = "h887-000"
      pfg-app-inventory-id = "no-entry"
      pfg-service-id       = "is.foundationalservices"
      pfg-repo-name        = var.repo_name
    }
  }
  ignore_tags {
    key_prefixes = ["foundation:"]
  }
}
