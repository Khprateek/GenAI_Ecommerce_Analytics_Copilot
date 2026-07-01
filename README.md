# GenAI-Powered Cloud Analytics Copilot for E-Commerce

A production-grade, end-to-end analytics platform built on a modern data stack.
Combines cloud-native warehousing, transformation pipelines, and AI-powered querying to deliver real business intelligence on e-commerce data.

---

## Architecture

```
Local CSV Files (7 tables, 500k+ rows)
        │
        ▼
Python Ingestion (pandas + BigQuery client)    ← no GCS bucket needed
        │
        ▼
BigQuery — dataset: raw
  raw.orders · raw.order_items · raw.products
  raw.customers · raw.events · raw.returns · raw.marketing_spend
        │
        ▼
dbt Transformation Pipeline
  ├── Layer 1: staging/        (type casting, renaming, filtering)
  ├── Layer 2: intermediate/   (joins, RFM scoring, enrichment)
  └── Layer 3: marts/
        ├── core/              (Star Schema: fact + 5 dims)
        └── metrics/           (pre-aggregated KPI tables)
        │
        ▼
BigQuery — dataset: metrics
  revenue_daily · customer_ltv · product_performance
  conversion_rate · marketing_performance
        │
        ▼
Streamlit Dashboard            ← Phase 1
  Overview · Products · Customers · Returns · Marketing · Funnel
        │
        ▼
Gemini API (Phase 2)           ← AI Copilot Layer
  Natural-language → SQL · Automated insights · Anomaly detection
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data Generation | Python (Faker) | Realistic synthetic e-commerce data |
| Ingestion | Python + BigQuery Client | CSV → BigQuery without GCS |
| Orchestration | Apache Airflow | DAG scheduling, dependency management |
| Warehouse | Google BigQuery | Cloud-native SQL analytics engine |
| Transformation | dbt-bigquery | Modular SQL models, tests, lineage |
| Dashboard | Streamlit + Plotly | Interactive analytics frontend |
| AI Copilot | Gemini 1.5 Pro | Natural-language SQL, insight generation |
| Infrastructure | Terraform (optional) | Dataset and IAM provisioning |

---

## Project Structure

```
ecommerce-analytics/
│
├── credentials/
│   └── gcp-key.json                  # Service account key (git-ignored)
│
├── data/
│   ├── generate_data.py              # Generates 7 CSVs via Faker
│   ├── orders.csv                    # 50,000 orders
│   ├── order_items.csv               # ~150,000 line items
│   ├── products.csv                  # 5,000 products with brand + cost
│   ├── customers.csv                 # 20,000 customers
│   ├── events.csv                    # 300,000 clickstream events
│   ├── returns.csv                   # ~2,500 return records
│   └── marketing_spend.csv           # ~6,000 daily spend rows by channel
│
├── bigquery/
│   └── setup_datasets.py             # Creates raw/staging/marts/metrics datasets
│
├── ingestion/
│   └── load_raw.py                   # Loads all CSVs → BigQuery raw (direct, no bucket)
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml                  # BigQuery connection via service account
│   ├── packages.yml                  # dbt-utils
│   │
│   ├── models/
│   │   ├── staging/                  # Layer 1: type-safe views over raw tables
│   │   │   ├── _sources.yml          # Source declarations + freshness tests
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_order_items.sql
│   │   │   ├── stg_products.sql      # Includes brand, cost_price, margin_pct
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_events.sql
│   │   │   ├── stg_returns.sql
│   │   │   └── stg_marketing_spend.sql
│   │   │
│   │   ├── intermediate/             # Layer 2: business logic + joins
│   │   │   ├── int_orders_enriched.sql     # Orders + items + customer context
│   │   │   ├── int_customer_orders.sql     # RFM scoring (recency/frequency/monetary)
│   │   │   └── int_product_revenue.sql     # Revenue + margin + return rate per product
│   │   │
│   │   └── marts/
│   │       ├── core/                 # Layer 3: Star schema (materialized tables)
│   │       │   ├── fact_orders.sql
│   │       │   ├── dim_customers.sql  # With RFM segments + value tiers
│   │       │   ├── dim_products.sql   # With margin, profit, return risk labels
│   │       │   ├── dim_date.sql       # Full date spine 2022–2027
│   │       │   ├── dim_channels.sql
│   │       │   └── _core_models.yml   # Column tests + documentation
│   │       │
│   │       └── metrics/              # Layer 4: Pre-aggregated KPIs
│   │           ├── revenue_daily.sql          # Net of returns + discounts
│   │           ├── customer_ltv.sql
│   │           ├── product_performance.sql
│   │           ├── conversion_rate.sql        # Daily event funnel
│   │           └── marketing_performance.sql  # ROAS, CAC, CTR by channel
│   │
│   ├── tests/
│   │   ├── assert_positive_revenue.sql
│   │   └── assert_no_orphan_orders.sql
│   │
│   └── macros/
│       └── safe_divide.sql
│
├── streamlit/
│   ├── app.py                        # Main dashboard (6 tabs)
│   ├── components/
│   │   ├── kpi_cards.py              # Gross revenue, net revenue, orders, AOV, returns
│   │   └── charts.py                 # Revenue, channel, margin, funnel, ROAS charts
│   └── utils/
│       ├── bq_client.py              # Cached BigQuery connection
│       └── queries.py                # All SQL strings (parameterised by date range)
│
├── airflow/
│   ├── docker-compose.yml            # Local Airflow via Docker
│   └── dags/
│       ├── ingestion_dag.py          # Schedules load_raw.py daily
│       └── dbt_dag.py                # Runs dbt run → dbt test → dbt docs
│
├── .env.example                      # Required environment variables
├── requirements.txt
└── README.md
```

---

## Quickstart

### Prerequisites

- Python 3.11+
- A Google Cloud project with BigQuery API enabled
- A service account with `BigQuery Admin` role → download JSON key
- (Optional) Docker Desktop for Airflow

### 1. Clone and install

```bash
git clone <your-repo>
cd ecommerce-analytics
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
cp .env.example .env
# Edit .env with your GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS path
export $(cat .env | xargs)
```

### 3. Generate synthetic data

```bash
cd data
python generate_data.py
# Produces 7 CSVs: 500k+ rows total
cd ..
```

### 4. Create BigQuery datasets

```bash
python bigquery/setup_datasets.py
# Creates: raw, staging, marts, metrics datasets in BigQuery
```

### 5. Load raw data into BigQuery

```bash
python ingestion/load_raw.py
# Direct CSV → BigQuery. No GCS bucket required.
```

### 6. Run dbt pipeline

```bash
cd dbt
dbt deps                  # installs dbt-utils
dbt run                   # 19 models: staging → intermediate → marts → metrics
dbt test                  # 40+ data quality tests
dbt docs generate && dbt docs serve   # browse lineage in browser
cd ..
```

### 7. Launch Streamlit dashboard

```bash
cd streamlit
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Dashboard Tabs

| Tab | What you see |
|---|---|
| 📈 Overview | Revenue trend (daily/weekly/monthly), breakdown by channel |
| 🏆 Products & Margin | Top 20 products, profit vs revenue by category, price tier |
| 👥 Customers | RFM segments (Champions → Lost), LTV distribution |
| ↩️ Returns | Return rate by product, refund amounts, high-risk items |
| 📣 Marketing | ROAS by channel, spend vs attributed revenue trend |
| 🔻 Funnel | Event-based conversion funnel (page view → cart → purchase) |

---

## dbt Model Lineage

```
raw sources (7 tables)
    │
    ▼
staging (7 views)          ← type-safe, renamed, filtered
    │
    ▼
intermediate (3 views)     ← RFM scoring, enrichment, aggregation
    │
    ├──────────────────────────────────────────────────┐
    ▼                                                  ▼
marts/core (5 tables)                         marts/metrics (5 tables)
fact_orders                                   revenue_daily
dim_customers                                 customer_ltv
dim_products                                  product_performance
dim_date                                      conversion_rate
dim_channels                                  marketing_performance
```

---

## Phase 2 — AI Copilot (Upcoming)

See [AI Implementation Roadmap](#ai-roadmap) below.

Planned additions:
- `streamlit/pages/ai_query.py` — natural-language to SQL via Gemini
- `streamlit/pages/ai_insights.py` — automated business commentary
- `ai/nl2sql.py` — prompt engineering for BigQuery SQL generation
- `ai/insights.py` — trend detection and anomaly summarisation

---

## AI Roadmap

### Phase 2A — Natural Language to SQL (4–6 weeks)

Enable users to ask questions in plain English and get BigQuery SQL + results back.

**How it works:**
1. User types: *"Which product category had the highest return rate last month?"*
2. Gemini receives the question + your full schema (table names, column names, descriptions from `_core_models.yml`)
3. Gemini generates valid BigQuery SQL
4. App runs SQL against BigQuery → shows table + chart
5. Gemini explains the result in 2–3 sentences

**Files to build:**
```
ai/
├── nl2sql.py            # Prompt template + Gemini API call
├── schema_context.py    # Extracts schema from dbt docs for the prompt
└── sql_validator.py     # Validates generated SQL before running it

streamlit/pages/
└── ai_query.py          # Chat-style UI: question → SQL → results → explanation
```

### Phase 2B — Automated Business Insights (2–3 weeks)

Gemini reads from `metrics.*` tables and writes weekly commentary automatically.

Examples it would generate:
- *"Revenue dropped 14% week-over-week, driven by a 32% decline in mobile channel orders."*
- *"Electronics category margin fell from 41% to 34% — likely due to increased returns from brand Voltix."*
- *"Customer acquisition cost on social rose to $18.40 vs $11.20 last month — ROAS below breakeven."*

### Phase 2C — Anomaly Detection (2–3 weeks)

Statistical alerts surfaced in the dashboard when KPIs deviate from normal ranges.

- Revenue anomalies (Z-score > 2.5 from 30-day rolling average)
- Sudden return rate spikes on specific products
- Conversion rate drops by channel
- Marketing spend efficiency degradation

### Phase 2D — Scheduled Report Generation (1–2 weeks)

Airflow DAG that runs every Monday morning:
1. Queries `metrics.*` for the past week
2. Sends data to Gemini with a "write an executive summary" prompt
3. Posts output to Slack / emails as HTML report

---

## Refinement Tasks (Build These to Deepen the Project)

### Data Engineering
1. **Incremental dbt models** — change `+materialized: table` to `incremental` for `fact_orders` and `revenue_daily`. Use `order_date` as the incremental key. This is how production pipelines work — full refresh doesn't scale.
2. **dbt snapshots** — add `snapshots/snap_customers.sql` to track slowly changing dimensions (customer segment changes over time).
3. **dbt source freshness** — add `loaded_at_field` and `freshness` thresholds to `_sources.yml` so `dbt source freshness` alerts you if raw data is stale.
4. **Schema tests on metrics** — add `dbt_utils.accepted_range` tests on `revenue_daily` (no negative revenue, no future dates).
5. **Airflow DAG hardening** — add retries, `on_failure_callback` (Slack alert), and SLA misses to both DAGs.

### Analytics & Modelling
6. **Cohort retention model** — build `marts/metrics/cohort_retention.sql` that shows what % of customers from each signup month are still ordering 1/3/6 months later.
7. **Product affinity model** — find products frequently bought together using `order_items`. Build `int_product_pairs.sql` and surface it as a "Frequently Bought Together" table.
8. **Customer churn prediction features** — build a feature table in dbt: `days_since_last_order`, `order_frequency_30d`, `avg_order_value_trend`. Feed this into a simple logistic regression in Python.
9. **Price elasticity analysis** — since `unit_price` drifts ±10% in the data generator, you can model how quantity sold changes with price.
10. **Seasonal decomposition** — run `statsmodels` seasonal decomposition on `revenue_daily` and surface trend vs seasonality components in a new Streamlit page.

### Dashboard
11. **Drill-down filters** — add `category`, `brand`, and `channel` multiselects to the sidebar so every chart responds to all filters simultaneously.
12. **Period-over-period comparison** — add a toggle to compare current period vs same period last year/last month. Show delta % on every chart.
13. **Export button** — add `st.download_button` to every dataframe so analysts can export to CSV with one click.
14. **Dark mode toggle** — Streamlit supports `.streamlit/config.toml` theming. Add a dark/light toggle in the sidebar.

### Infrastructure & Production
15. **Terraform for BigQuery** — write `infra/bigquery_datasets.tf` to provision datasets and IAM bindings as code.
16. **GitHub Actions CI** — add `.github/workflows/dbt_ci.yml` that runs `dbt compile` and `dbt test` on every pull request against a dev BigQuery dataset.
17. **Secrets via Secret Manager** — replace hardcoded service account file path with GCP Secret Manager lookups in `load_raw.py` and `bq_client.py`.
18. **Partitioned BigQuery tables** — add `partition_by` config to `fact_orders` dbt model so BigQuery partitions by `order_date`. Massive query cost reduction.

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `GCP_PROJECT_ID` | Your GCP project ID | `my-ecom-project-123` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | `/home/user/creds/key.json` |
| `BQ_LOCATION` | BigQuery dataset location | `US` (default) |
| `DATA_DIR` | Path to CSV files | `../data` (default) |

---

## Acknowledgements

Built as a learning project to demonstrate modern data stack skills:
dbt · BigQuery · Airflow · Streamlit · Gemini API · Python

---

*Phase 1: Analytics Foundation — complete*
*Phase 2: AI Copilot — in progress*
