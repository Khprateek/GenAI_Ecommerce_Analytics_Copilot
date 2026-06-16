import os
from google.cloud import bigquery
from google.oauth2 import service_account

# Config

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

DATASETS = {
    "raw": "Raw source data",
    "staging": "dbt staging layer",
    "marts": "Analytics/star schema layer",
    "metrics": "Business KPI layer"
}

# Validation

if not PROJECT_ID:
    raise ValueError(
        "GCP_PROJECT_ID environment variable is not set."
    )
if not CREDENTIALS_PATH:
    raise ValueError(
        "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set."
    )
if not os.path.exists(CREDENTIALS_PATH):
    raise FileNotFoundError(
        f"Credentials file not found: {CREDENTIALS_PATH}"
    )

# BigQuery Client

credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH
)

client = bigquery.Client(
    project = PROJECT_ID,
    credentials=credentials
)

# Create Datasets

def create_dataset(dataset_id: str, description: str):
    dataset_ref = f"{PROJECT_ID}.{dataset_id}"

    try:
        client.get_dataset(dataset_ref)
        print(f"[EXISTS] Dataset already exists: {dataset_id}")

    except Exception:
        dataset = bigquery.Dataset(dataset_ref)

        dataset.location = "US"
        dataset.description = description

        client.create_dataset(dataset)

        print(f"[CREATED] Dataset created: {dataset_id}")


# Main

if __name__ == "__main__":
    print("\nSetting up BigQuery datasets...\n")
    for dataset_id, description in DATASETS.items():
        create_dataset(dataset_id, description)

    print("\nDataset setup Complete.")