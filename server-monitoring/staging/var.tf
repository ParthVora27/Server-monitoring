variable "repo_name" {
  type        = string
  description = "The repository name that manages the resources."
  default     = "no-entry"
}

variable "source_account_ids" {
  type        = list(string)
  description = "source account ids"
  default     = ["295738771512"]
}

variable "metric_report_lambda_account_ids" {
  type        = string
  description = "source account ids"
  default     = "295738771512"
}
