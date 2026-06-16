output "datasets_created" {
  value = [
    google_bigquery_dataset.raw.dataset_id,
    google_bigquery_dataset.staging.dataset_id,
    google_bigquery_dataset.marts.dataset_id,
    google_bigquery_dataset.metrics.dataset_id
  ]
}