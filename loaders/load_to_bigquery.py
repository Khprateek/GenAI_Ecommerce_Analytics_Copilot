import os
import logging
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# =====================================================
# Configuration
# =====================================================

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

RAW_DATASET = "raw"

TABLES = [
    "customers",
    "products",
    "orders",
    "order_items",
    "events"
]

DATA_DIR = Path("data/raw")

# =====================================================
# Logging
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("bigquery_loader")

# =====================================================
# Validation
# =====================================================

if not PROJECT_ID:
    raise ValueError(
        "Environment variable GCP_PROJECT_ID is not set."
    )

if not CREDENTIALS_PATH:
    raise ValueError(
        "Environment variable GOOGLE_APPLICATION_CREDENTIALS is not set."
    )

if not os.path.exists(CREDENTIALS_PATH):
    raise FileNotFoundError(
        f"Credentials file not found: {CREDENTIALS_PATH}"
    )

# =====================================================
# BigQuery Client
# =====================================================

credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH
)

client = bigquery.Client(
    project=PROJECT_ID,
    credentials=credentials
)

# =====================================================
# Helper Functions
# =====================================================

def load_table(table_name: str) -> None:
    """
    Load a CSV file into BigQuery raw dataset.
    """

    csv_path = DATA_DIR / f"{table_name}.csv"

    if not csv_path.exists():
        logger.warning(f"File not found: {csv_path}")
        return

    logger.info(f"Reading {csv_path}")

    df = pd.read_csv(csv_path)

    logger.info(
        f"{table_name}: {len(df):,} rows loaded from CSV"
    )

    destination_table = (
        f"{PROJECT_ID}.{RAW_DATASET}.{table_name}"
    )

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True
    )

    load_job = client.load_table_from_dataframe(
        dataframe=df,
        destination=destination_table,
        job_config=job_config
    )

    load_job.result()

    table = client.get_table(destination_table)

    logger.info(
        f"{table_name}: "
        f"{table.num_rows:,} rows written to BigQuery"
    )


# =====================================================
# Main
# =====================================================

def main():

    logger.info("=" * 60)
    logger.info("Starting BigQuery Load")
    logger.info("=" * 60)

    for table in TABLES:

        try:
            load_table(table)

        except Exception as e:

            logger.exception(
                f"Failed loading table {table}: {e}"
            )

    logger.info("=" * 60)
    logger.info("BigQuery Load Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()