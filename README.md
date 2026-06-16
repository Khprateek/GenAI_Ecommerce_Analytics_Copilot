# GenAI-Powered Cloud Analytics Copilot

E-commerce analytics pipeline using:

- Python
- BigQuery
- Airflow
- dbt
- Streamlit

Export : 
export GCP_PROJECT_ID="genai-copilot-enterprisedata"
export GOOGLE_APPLICATION_CREDENTIALS="D:/JOB/Work/GenAI-Powered Cloud Analytics Copilot for E-Commerce Data Warehousing/genai-copilot-enterprisedata.json"


# data Flow
Local CSV Files
      │
      ▼
Google Cloud Storage
      │
      ▼
BigQuery (raw_ecommerce)
      │
      ▼
dbt
      │
      ▼
stg_ecommerce
      │
      ▼
mart_ecommerce
      │
      ▼
metrics_ecommerce