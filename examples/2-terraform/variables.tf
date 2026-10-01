variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources in"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "The GCP zone to deploy VM instances in (defaults to <region>-a)"
  type        = string
  default     = ""
}
