# Input Variables for Terraform GCP Provisioning

variable "gcp_project_id" {
  type        = string
  description = "GCP Project ID for deployment"
  default     = "enterprise-data-ai-platform"
}

variable "gcp_region" {
  type        = string
  description = "GCP Region for Cloud Run and Storage"
  default     = "us-central1"
}

variable "environment" {
  type        = string
  description = "Deployment environment (development, staging, production)"
  default     = "production"
}
