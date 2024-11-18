variable "repo_name" {
  type        = string
  description = "The repository name that manages the resources."
  default     = "no-entry"
}

variable "source_account_ids" {
  type        = list(string)
  description = "source account ids"
  default     = ["415991856277", "661714083946", "663779911812"]
}

variable "metric_report_lambda_account_ids" {
  type        = string
  description = "source account ids"
  default     = "415991856277,865646183926,992317999197"
}
