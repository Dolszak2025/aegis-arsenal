terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  default     = "europe-west1"
  type        = string
}

# Pub/Sub Topic
resource "google_pubsub_topic" "aegis_pubsub_topic" {
  name = "aegis-pubsub-topic"
}

# Dead Letter Queue Topic (for failed messages)
resource "google_pubsub_topic" "aegis_dlq_topic" {
  name = "aegis-dlq-topic"
}

# Subscription for the main topic
resource "google_pubsub_subscription" "aegis_subscription" {
  name  = "aegis-subscription"
  topic = google_pubsub_topic.aegis_pubsub_topic.name

  ack_deadline_seconds = 60

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.aegis_dlq_topic.id
    max_delivery_attempts = 5
  }
}

# Service Account for Cloud Function
resource "google_service_account" "aegis_bot_sa" {
  account_id   = "aegis-bot-sa"
  display_name = "Aegis Bot Service Account"
}

# IAM Bindings for Service Account
resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.aegis_bot_sa.email}"
}

resource "google_project_iam_member" "pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.aegis_bot_sa.email}"
}

resource "google_project_iam_member" "logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.aegis_bot_sa.email}"
}

resource "google_project_iam_member" "trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.aegis_bot_sa.email}"
}

# Secret Manager for API Keys
resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai-api-key"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "anthropic_api_key" {
  secret_id = "anthropic-api-key"
  replication {
    automatic = true
  }
}

# Grant access to secrets for the service account
resource "google_secret_manager_secret_iam_member" "openai_secret_access" {
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.aegis_bot_sa.email}"
}

# Cloud Scheduler for Resilience Drills
resource "google_cloud_scheduler_job" "aegis_resilience_drill" {
  name        = "aegis-resilience-drill"
  description = "Scheduled job to trigger resilience drills for Aegis Arsenal"
  schedule    = "0 2 * * *"  # Every day at 2 AM
  time_zone   = "UTC"

  pubsub_target {
    topic_name = google_pubsub_topic.aegis_pubsub_topic.id
    data       = base64encode(jsonencode({
      message = {
        data = base64encode("$$SSC_RESILIENCE_DRILL_ACTIVE: Simulate failure for checkpointer test").data
        messageId = "resilience-drill-${timestamp()}"
        attributes = {
          drill_type = "RESILIENCE_TEST"
        }
      }
    }))
  }

  depends_on = [google_pubsub_topic.aegis_pubsub_topic]
}