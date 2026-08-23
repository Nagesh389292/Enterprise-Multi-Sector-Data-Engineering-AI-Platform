# Declarative GCP Resource Provisioning (Cloud Run, Cloud Storage, BigQuery, Secret Manager)

# 1. Cloud Storage Medallion Lakehouse Buckets
resource "google_storage_bucket" "bronze_lake" {
  name                     = "${var.gcp_project_id}-lake-bronze"
  location                 = var.gcp_region
  force_destroy            = true
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "silver_lake" {
  name                     = "${var.gcp_project_id}-lake-silver"
  location                 = var.gcp_region
  force_destroy            = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "gold_lake" {
  name                     = "${var.gcp_project_id}-lake-gold"
  location                 = var.gcp_region
  force_destroy            = true
  uniform_bucket_level_access = true
}

# 2. BigQuery Gold Analytics Dataset
resource "google_bigquery_dataset" "analytics_gold" {
  dataset_id                  = "enterprise_platform_gold"
  friendly_name               = "Enterprise Multi-Sector Gold Data Marts"
  description                 = "Gold Data Marts across Credit Card, Banking, Healthcare, Clinical, Insurance, and Retail"
  location                    = var.gcp_region
  default_table_expiration_ms = 3600000000
}

# 3. GCP Cloud Run Backend Service
resource "google_cloud_run_service" "api_backend" {
  name     = "enterprise-platform-api"
  location = var.gcp_region

  template {
    spec {
      containers {
        image = "gcr.io/${var.gcp_project_id}/enterprise-backend:latest"

        resources {
          limits = {
            memory = "2Gi"
            cpu    = "2000m"
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.gcp_project_id
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow public access to Cloud Run API Service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.api_backend.location
  project  = google_cloud_run_service.api_backend.project
  service  = google_cloud_run_service.api_backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
