# GCP Cost Safeguards & Budget Notification Infrastructure

resource "google_monitoring_notification_channel" "email_alert" {
  display_name = "Cloud Platform Engineering Budget Notification Channel"
  type         = "email"
  labels = {
    email_address = "admin@enterprise-analytics.com"
  }
}

resource "google_billing_budget" "monthly_free_tier_budget" {
  billing_account = "000000-000000-000000"
  display_name    = "Enterprise Analytics Monthly Free Tier Safeguard ($5 Threshold)"

  budget_filter {
    projects = ["projects/${var.gcp_project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "5"
    }
  }

  threshold_rules {
    threshold_percent = 0.5 # Alert at $2.50
  }
  threshold_rules {
    threshold_percent = 0.9 # Alert at $4.50
  }
  threshold_rules {
    threshold_percent = 1.0 # Alert at $5.00
  }

  all_updates_rule {
    monitoring_notification_channels = [
      google_monitoring_notification_channel.email_alert.id
    ]
    disable_default_feedback_label = false
  }
}
