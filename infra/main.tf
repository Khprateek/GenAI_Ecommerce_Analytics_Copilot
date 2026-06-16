terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_bigquery_dataset" "raw" {
  dataset_id = "raw"
  location   = "US"

  description = "Raw source data"
}

resource "google_bigquery_dataset" "staging" {
  dataset_id = "staging"
  location   = "US"

  description = "dbt staging layer"
}

resource "google_bigquery_dataset" "marts" {
  dataset_id = "marts"
  location   = "US"

  description = "Star schema layer"
}

resource "google_bigquery_dataset" "metrics" {
  dataset_id = "metrics"
  location   = "US"

  description = "KPI aggregate tables"
}