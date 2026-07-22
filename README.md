# GenAI-Powered Cloud Analytics Copilot for Quick-Commerce Data Warehousing

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![BigQuery](https://img.shields.io/badge/BigQuery-Cloud_DWH-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/bigquery)
[![dbt](https://img.shields.io/badge/dbt-Data_Modeling-FF694B?style=for-the-badge&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Airflow](https://img.shields.io/badge/Airflow-Orchestration-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white)](https://airflow.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/Gemini_AI-Copilot-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

> An end-to-end Modern Data Stack analytics platform built around India's quick-commerce model (Zepto-style 10-minute delivery). The system generates realistic operational data, loads it into Google BigQuery, transforms it through a professional dbt pipeline (staging → intermediate → star schema), powers an executive BI dashboard with embedded churn prediction, and includes a schema-grounded natural language SQL copilot using Gemini AI.

---

## Table of Contents

- [Architecture](#architecture)
- [Data Model](#data-model)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [dbt Pipeline](#dbt-pipeline)
- [Dashboard Features](#dashboard-features)
- [AI Analytics Copilot](#ai-analytics-copilot)
- [Orchestration](#orchestration)

---

## Architecture

The project follows a standard Modern Data Stack (MDS) pipeline, heavily integrated with Google Cloud and AI:

1. **Data Generation & Ingestion**: Python Faker scripts simulate a fast-paced Zepto-style quick commerce dataset, dumping raw operational CSVs which are immediately ingested into BigQuery.
2. **Data Warehouse & Transformation**: Google BigQuery serves as the scalable backend, while `dbt Core` builds out a multi-layered transformation pipeline:
   - **Staging Layer**: Validates types, cleanses data, and sets schemas.
   - **Intermediate Layer**: Enriches orders, handles RFM (Recency, Frequency, Monetary) computations, and extracts churn features.
   - **Marts (Core)**: Exposes the primary analytical star schema (1 Fact table with 5 Dimension tables).
   - **Marts (Metrics)**: Pre-aggregated BI tables for extremely fast dashboard rendering.
3. **Serving Layer**: A Streamlit application provides a multi-tab BI dashboard. It interfaces with `scikit-learn` for ML-driven churn prediction, and utilizes Google's **Gemini AI** to act as a schema-grounded natural language SQL copilot.

---

## Data Model

The dataset simulates a **Zepto-inspired quick-commerce** operation across 16 Indian metro/tier-1 cities with dark stores, delivery riders, and a grocery/daily-essentials catalog.

### Raw Tables (9 tables)

| Table | Rows | Description |
|---|---|---|
| `dark_stores` | ~59 | Micro-fulfilment center locations with SKU capacity and delivery radius |
| `delivery_partners` | ~1,500 | Riders assigned to dark stores with vehicle types |
| `customers` | 20,000 | Customer profiles with Zepto Pass membership and home store |
| `products` | 5,000 | Grocery catalog with MRP, selling price, cost price, perishability |
| `orders` | 50,000 | Order headers with delivery promise, actual time, payment, platform |
| `order_items` | ~180,000 | Line items with quantity, unit price, substitution flag |
| `order_issues` | ~1,300 | Same-day issue resolution (no traditional "returns") |
| `events` | 300,000 | App/web clickstream (page_view, add_to_cart, reorder_click, purchase) |
| `marketing_spend` | ~6,500 | Daily spend across 5 acquisition channels |

### Star Schema (marts/core)

The core analytical schema follows a traditional dimensional model centered around a single unified fact table:

- **`fact_orders`** (Center): Connects to all dimensions via surrogate keys (`_sk`), storing INR financials, delivery KPIs, and basket metrics.
- **`dim_customers`**: RFM segments, value tiers, churn risk tiers, and Zepto Pass membership.
- **`dim_dark_stores`**: City/locality geography, operational volume tiers, and delivery performance tiers.
- **`dim_delivery_partners`**: Rider vehicle types, historical performance tiers, and experience levels.
- **`dim_products`**: Category naming, pricing tiers, margin health, and sales performance tags.
- **`dim_date`**: Calendar spine with Indian fiscal year (Apr-Mar) layouts and analytical flags.

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **Data Generation** | Python, Faker (`en_IN`) | Simulates Zepto-style quick-commerce operational data |
| **Ingestion** | Python, `google-cloud-bigquery` | Batch loads CSVs into BigQuery `raw` dataset |
| **Data Warehouse** | Google BigQuery | Serverless, columnar cloud warehouse |
| **Data Modeling** | dbt Core 1.11+ | Staging → Intermediate → Star Schema → Metrics |
| **Orchestration** | Apache Airflow | DAG-based scheduling for ingestion and dbt runs |
| **Dashboard** | Streamlit, Plotly | Multi-tab executive BI dashboard |
| **Machine Learning** | scikit-learn | Logistic Regression churn prediction model |
| **Generative AI** | Gemini 1.5 Pro | Schema-grounded NL-to-SQL copilot with insight generation |

---

## Project Structure

```text
├── data/
│   ├── generate_data.py                # Zepto-style dataset generator (9 tables)
│   └── raw/                            # Generated CSV files
│
├── loaders/
│   ├── load_to_bigquery.py             # CSV → BigQuery ingestion (autodetect)
│   └── setup_datasets.py              # Provisions raw/staging/marts datasets
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── packages.yml                    # dbt_utils dependency
│   ├── macros/
│   │   ├── generate_schema_name.sql
│   │   └── safe_divide.sql
│   └── models/
│       ├── staging/                    # Layer 1: Type casting & validation
│       │   ├── _sources.yml
│       │   ├── stg_orders.sql
│       │   ├── stg_order_items.sql
│       │   ├── stg_customers.sql
│       │   ├── stg_products.sql
│       │   ├── stg_dark_stores.sql
│       │   ├── stg_delivery_partners.sql
│       │   ├── stg_order_issues.sql
│       │   ├── stg_events.sql
│       │   └── stg_marketing_spend.sql
│       ├── intermediate/               # Layer 2: Business logic & feature engineering
│       │   ├── int_orders_enriched.sql
│       │   ├── int_customer_orders.sql
│       │   ├── int_customer_churn_features.sql
│       │   └── int_product_revenue.sql
│       └── marts/
│           ├── core/                   # Layer 3: Star schema
│           │   ├── _core_models.yml
│           │   ├── fact_orders.sql
│           │   ├── dim_customers.sql
│           │   ├── dim_products.sql
│           │   ├── dim_dark_stores.sql
│           │   ├── dim_delivery_partners.sql
│           │   └── dim_date.sql
│           └── metrics/                # Layer 4: Pre-aggregated BI tables
│               ├── revenue_daily.sql
│               ├── customer_ltv.sql
│               ├── product_performance.sql
│               ├── marketing_performance.sql
│               ├── conversion_rate.sql
│               └── funnel_stages.sql
│
├── airflow/
│   └── dags/
│       ├── ingestion_dag.py            # Schedules data generation + BigQuery load
│       └── dbt_dag.py                  # Runs dbt build + test pipeline
│
├── streamlit/
│   ├── Dashboard.py                    # Main multi-tab Streamlit application
│   ├── pages/
│   │   ├── Analytics_copilot.py        # AI-powered natural language querying
│   │   └── Pipeline_health.py          # dbt pipeline monitoring
│   ├── components/
│   │   ├── charts.py                   # Plotly chart configurations
│   │   └── kpi_cards.py                # Custom KPI card components
│   ├── utils/
│   │   ├── bq_client.py                # BigQuery connection wrapper
│   │   ├── queries.py                  # SQL query library for dashboard tabs
│   │   ├── churn_model.py              # Logistic Regression training & inference
│   │   └── health_check.py             # Pipeline health monitoring utilities
│   └── ai/
│       ├── gemini_client.py            # Gemini API wrapper
│       ├── schema_context.py           # Dynamic dbt schema extraction
│       ├── prompt_builder.py           # Prompt engineering for SQL generation
│       ├── prompts.py                  # Prompt templates
│       ├── ai_sql_generator.py         # Question → SQL translation
│       ├── ai_sql_validator.py         # SQL injection & syntax validation
│       ├── insight_generator.py        # Executive summary generation
│       └── response_parser.py          # Gemini response parsing
│
├── .env.example                        # Environment variable template
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python **3.11+**
- A GCP project with the **BigQuery API** enabled
- A service account JSON with `BigQuery Admin` permissions
- dbt Core **1.11+** with the `dbt-bigquery` adapter

### 1. Clone & Install

```bash
git clone <repository_url>
cd GenAI-Powered-Cloud-Analytics-Copilot
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env         # Linux/Mac: cp .env.example .env
```

Edit `.env` with your GCP project ID and path to the service account JSON:

```env
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Generate & Load Data

```bash
python data/generate_data.py
python loaders/setup_datasets.py
python loaders/load_to_bigquery.py
```

### 4. Run dbt Pipeline

```bash
cd dbt
dbt deps
dbt run
dbt test
cd ..
```

### 5. Launch Dashboard

```bash
cd streamlit
streamlit run Dashboard.py
```

Open `http://localhost:8501` to access the dashboard and AI Copilot.

---

## dbt Pipeline

The dbt project follows the **staging → intermediate → marts** layered architecture:

### Layer Breakdown

| Layer | Materialization | Dataset | Purpose |
|---|---|---|---|
| **Staging** | `view` | `staging` | Type casting, cleaning, null filtering — no business logic |
| **Intermediate** | `view` | `staging` | Enriched orders, RFM scoring, churn features, product profitability |
| **Marts: Core** | `table` | `marts` | Star schema: 1 fact table + 5 dimension tables |
| **Marts: Metrics** | `table` | `metrics` | Pre-aggregated tables optimized for dashboard queries |

### Key Intermediate Models

| Model | Purpose |
|---|---|
| `int_orders_enriched` | Joins all 6 staging models into a single wide order fact with delivery KPIs, basket tiers, and INR financials |
| `int_customer_orders` | Customer-level RFM scoring with 8 segments (Champions → Lost Customers) |
| `int_customer_churn_features` | Feature vector comparing lifetime vs last-30-day behaviour for churn prediction |
| `int_product_revenue` | Product profitability with margin analysis, substitution rates, and velocity metrics |

### Quick-Commerce KPIs Tracked

- **Delivery Performance**: Promised vs actual delivery time, on-time %, delay buckets (0-10 / 11-15 / 16-20 / 20+ min)
- **Dark Store Operations**: Order volume, rider fleet composition, delivery performance tier per store
- **Basket Economics**: AOV, basket size tiers (Micro/Small/Medium/Large), discount depth
- **Customer Health**: RFM segments, churn risk tiers, Zepto Pass impact, issue rates
- **Product Quality**: Substitution rates, issue rates per product, margin health, velocity (units/day)

---

## Dashboard Features

### Multi-Tab Executive Dashboard

| Tab | Key Metrics |
|---|---|
| **Overview** | Revenue trends, order velocity, AOV, delivery on-time rate, fulfilment rate |
| **Products** | Category performance, margin health, substitution rates, top/bottom sellers |
| **Customers** | RFM segmentation, value tiers, churn risk distribution, pass member analysis |
| **Marketing** | Channel-level spend, ROAS, CAC, cost-per-install, click-through rates |
| **Funnel** | Page view → Add to cart → Reorder click → Purchase conversion rates |
| **Pipeline Health** | dbt model status, data freshness, row counts, test results |

### Predictive Churn Modeling

- **Feature Engineering**: dbt intermediate models compute AOV trends, delivery experience trends, issue rate changes, and app engagement metrics over a 30-day window
- **Model**: scikit-learn Logistic Regression with `StandardScaler` normalization
- **Risk Tiers**: Active / Medium Risk / High Risk / Churned / Dormant
- **Business Output**: At-risk LTV quantification and top high-risk customer profiles

---

## AI Analytics Copilot

The copilot translates natural language business questions into validated BigQuery SQL, executes them, and generates executive-ready insights.

**Example queries:**
- *"Which dark store had the highest on-time delivery rate last month?"*
- *"Show me revenue trend by category for Q1 2025"*
- *"What is the average delivery time for pass members vs non-pass members?"*

### Query Execution Flow

1. **User asks question**: E.g., *"What was the conversion rate trend last month?"*
2. **Schema context loading**: The app dynamically fetches the latest tables, columns, and relationships from the dbt models.
3. **AI SQL Generation**: Gemini API receives the prompt (question + schema context) and generates syntactically valid BigQuery SQL.
4. **Validation**: Internal validator checks for SQL injection, `DROP/DELETE` statements, and syntax errors.
5. **Execution**: Validated SQL executes securely on BigQuery, returning a Pandas DataFrame.
6. **Insight Generation**: The raw DataFrame + original question are passed back to Gemini, which generates a natural language executive summary.
7. **Rendering**: The UI displays the raw data table, an interactive Plotly chart, and the AI-generated insights.

---

## Orchestration

Two Airflow DAGs manage the daily pipeline:

| DAG | Schedule | Workflow |
|---|---|---|
| **Ingestion DAG** | Daily | Task 1: Generate synthetic data → Task 2: Load to BigQuery `raw` dataset |
| **dbt DAG** | Triggered by Ingestion DAG | Task 1: `dbt run` → Task 2: `dbt test` → Task 3: `dbt docs generate` |

---

<p align="center">
  Built with ☕ and BigQuery from India
</p>
