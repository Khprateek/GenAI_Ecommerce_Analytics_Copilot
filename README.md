# GenAI-Powered Cloud Analytics Copilot

E-commerce analytics pipeline using:

- Python
- BigQuery
- Airflow
- dbt
- Streamlit


# data flow
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


