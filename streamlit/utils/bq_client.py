import os
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

@st.cache_resource   # runs once, reuses across all reruns
def get_client() -> bigquery.Client:
    """Returns a cached BigQuery client using service account credentials."""
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    return bigquery.Client(
        credentials=creds,
        project=os.environ["GCP_PROJECT_ID"]
    )

@st.cache_data(ttl=300)   # cache query results for 5 minutes
def run_query(sql: str) -> pd.DataFrame:
    """Run a SQL query and return a pandas DataFrame. Results cached 5 mins."""
    client = get_client()
    return client.query(sql).to_dataframe()