# Terraform Deployment Outputs

output "cloud_run_service_url" {
  value       = google_cloud_run_service.api_backend.status[0].url
  description = "Public URL for deployed GCP Cloud Run API Backend Service"
}

output "gcs_bronze_bucket" {
  value       = google_storage_bucket.bronze_lake.name
  description = "GCS Bronze Lakehouse Bucket Name"
}

output "gcs_gold_bucket" {
  value       = google_storage_bucket.gold_lake.name
  description = "GCS Gold Lakehouse Bucket Name"
}

output "bigquery_dataset_id" {
  value       = google_bigquery_dataset.analytics_gold.dataset_id
  description = "BigQuery Analytics Dataset ID"
}
