import streamlit as st
import pandas as pd
from utils.health_check import get_table_health

# Helper function to render HTML safely without markdown parser code-block indentation bugs
def render_html(html_str: str):
    cleaned_html = "\n".join([line.strip() for line in html_str.split("\n")])
    st.markdown(cleaned_html, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Pipeline Health Dashboard",
    page_icon="🩺",
    layout="wide",
)

# Custom styling for premium design
render_html("""
<style>
    /* Status banner */
    .status-banner {
        padding: 24px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Glowing pulse animation */
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 var(--pulse-color);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
        }
    }
    
    .pulse-dot {
        border-radius: 50%;
        display: inline-block;
        height: 14px;
        width: 14px;
        margin-right: 12px;
        animation: pulse 2s infinite;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #1e1e24;
        border: 1px solid #2e2e38;
        border-radius: 12px;
        padding: 20px;
        text-align: left;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 5px 0;
        background: linear-gradient(45deg, #f4f4f5, #a1a1aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-lbl {
        font-size: 0.85rem;
        color: #71717a;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #a1a1aa;
        margin-top: 5px;
    }
</style>
""")

st.title("🩺 Data Pipeline Health Dashboard")
st.caption("Real-time telemetry and validation of the e-commerce staging layer (BigQuery → dbt)")
st.markdown("---")

# Fetch health data from BigQuery
with st.spinner("Fetching pipeline telemetry from BigQuery..."):
    df = get_table_health()

# Process statuses
has_error = any(df['Status'] == '❌')
has_warning = any(df['Status'] == '⚠️')
total_rows = sum(df['raw_rows'])
alerts_count = sum(df['Status'] != '✅')

if has_error:
    status_title = "System Alert"
    status_desc = "One or more tables have critical issues. Immediate action required."
    status_bg = "rgba(239, 68, 68, 0.08)"
    status_border = "1px solid rgba(239, 68, 68, 0.25)"
    status_color = "#ef4444"
    pulse_color = "rgba(239, 68, 68, 0.6)"
    text_color = "#fca5a5"
elif has_warning:
    status_title = "Degraded Operational Status"
    status_desc = "Minor data validation anomalies detected. System remains operational."
    status_bg = "rgba(245, 158, 11, 0.08)"
    status_border = "1px solid rgba(245, 158, 11, 0.25)"
    status_color = "#f59e0b"
    pulse_color = "rgba(245, 158, 11, 0.6)"
    text_color = "#fde047"
else:
    status_title = "All Systems Operational"
    status_desc = "All monitored tables are healthy. Data validation tests passing."
    status_bg = "rgba(16, 185, 129, 0.08)"
    status_border = "1px solid rgba(16, 185, 129, 0.25)"
    status_color = "#10b981"
    pulse_color = "rgba(16, 185, 129, 0.6)"
    text_color = "#a7f3d0"

# 1. Overall Pipeline Status (Top Banner)
render_html(f"""
<div class="status-banner" style="background-color: {status_bg}; border: {status_border};">
    <div style="display: flex; align-items: center;">
        <span class="pulse-dot" style="background-color: {status_color}; --pulse-color: {pulse_color};"></span>
        <div>
            <div style="font-weight: 700; font-size: 1.25rem; color: {text_color};">{status_title}</div>
            <div style="font-size: 0.9rem; color: #a1a1aa; margin-top: 2px;">{status_desc}</div>
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 0.8rem; color: #71717a; text-transform: uppercase;">Last Telemetry Sync</div>
        <div style="font-weight: 600; color: #e4e4e7; font-size: 1.0rem; margin-top: 2px;">Just Now</div>
    </div>
</div>
""")

# Metric Row
c1, c2, c3, c4 = st.columns(4)

with c1:
    health_score = int(((len(df) - alerts_count) / len(df)) * 100) if len(df) > 0 else 0
    render_html(f"""
    <div class="metric-card">
        <div class="metric-lbl">Pipeline Health</div>
        <div class="metric-val">{health_score}%</div>
        <div class="metric-sub">✓ {len(df) - alerts_count} of {len(df)} tables healthy</div>
    </div>
    """)

with c2:
    render_html(f"""
    <div class="metric-card">
        <div class="metric-lbl">Total Records</div>
        <div class="metric-val">{total_rows:,}</div>
        <div class="metric-sub">Across monitored tables</div>
    </div>
    """)

with c3:
    render_html(f"""
    <div class="metric-card">
        <div class="metric-lbl">Active Alerts</div>
        <div class="metric-val" style="color: {status_color}; -webkit-text-fill-color: initial;">{alerts_count}</div>
        <div class="metric-sub">Anomalies requiring review</div>
    </div>
    """)

with c4:
    render_html("""
    <div class="metric-card">
        <div class="metric-lbl">Ingestion Mode</div>
        <div class="metric-val">Batch</div>
        <div class="metric-sub">Scheduled frequency: 5m</div>
    </div>
    """)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📊 Table-Level Validation Details")

# 2. Table Health Custom HTML Table
table_rows_html = ""
for _, r in df.iterrows():
    tbl = r['Table']
    rows_val = r['Rows']
    freshness = r['Freshness']
    null_pct = r['Null %']
    duplicates = r['Duplicates']
    status = r['Status']
    
    # Format status badge
    if status == '✅':
        badge_html = '<span style="background-color: rgba(16, 185, 129, 0.12); color: #34d399; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.2);">✅ Healthy</span>'
    elif status == '⚠️':
        badge_html = '<span style="background-color: rgba(245, 158, 11, 0.12); color: #fbbf24; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(245, 158, 11, 0.2);">⚠️ Warning</span>'
    else:
        badge_html = '<span style="background-color: rgba(239, 68, 68, 0.12); color: #f87171; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(239, 68, 68, 0.2);">❌ Error</span>'
        
    table_rows_html += f"""
    <tr style="border-bottom: 1px solid #2e2e38; transition: background-color 0.2s;">
        <td style="padding: 16px 20px; font-weight: 600; color: #f4f4f5; font-size: 0.95rem; font-family: monospace;">{tbl}</td>
        <td style="padding: 16px 20px; color: #e4e4e7; text-align: right; font-family: monospace;">{rows_val}</td>
        <td style="padding: 16px 20px; color: #e4e4e7; font-family: monospace;">{freshness}</td>
        <td style="padding: 16px 20px; color: #e4e4e7; text-align: right; font-family: monospace;">{null_pct}</td>
        <td style="padding: 16px 20px; color: #e4e4e7; text-align: right; font-family: monospace;">{duplicates}</td>
        <td style="padding: 16px 20px; text-align: center;">{badge_html}</td>
    </tr>
    """

render_html(f"""
<div style="overflow-x: auto; border: 1px solid #2e2e38; border-radius: 12px; background-color: #1e1e24; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
  <table style="width: 100%; border-collapse: collapse; text-align: left; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <thead>
      <tr style="background-color: #18181b; border-bottom: 2px solid #2e2e38;">
        <th style="padding: 16px 20px; font-weight: 600; color: #a1a1aa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Table</th>
        <th style="padding: 16px 20px; font-weight: 600; color: #a1a1aa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; text-align: right;">Rows</th>
        <th style="padding: 16px 20px; font-weight: 600; color: #a1a1aa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Freshness</th>
        <th style="padding: 16px 20px; font-weight: 600; color: #a1a1aa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; text-align: right;">Null %</th>
        <th style="padding: 16px 20px; font-weight: 600; color: #a1a1aa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; text-align: right;">Duplicates</th>
        <th style="padding: 16px 20px; font-weight: 600; color: #a1a1aa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; text-align: center;">Status</th>
      </tr>
    </thead>
    <tbody>
      {table_rows_html}
    </tbody>
  </table>
</div>
""")

st.markdown("<br><br>", unsafe_allow_html=True)
st.subheader("🔍 Deep-Dive Table Schemas & Checks")

# Staging Details Expanders
with st.expander("📝 orders (staging.stg_orders)") as exp:
    st.markdown("""
    **Description**: Cleaned & structured table representing sales orders. Casts timestamps, enforces types, and removes negative revenues.
    
    - **Primary Key**: `order_id` (enforced unique)
    - **Staging Schema & Casting Rules**:
      - `order_id` (STRING)
      - `customer_id` (STRING)
      - `order_date` (DATE)
      - `updated_at` (TIMESTAMP)
      - `order_status` (STRING) - Standardized (COMPLETED, REFUNDED, CANCELLED)
      - `revenue_usd` (NUMERIC) - Non-negative constraint
      - `discount_usd` (NUMERIC)
      - `shipping_cost_usd` (NUMERIC)
    - **Active Validation Rules**:
      - `order_id` must be unique.
      - `order_id`, `customer_id`, `order_date` must not be null.
      - `revenue_usd` must be >= 0.
    """)

with st.expander("👤 customers (staging.stg_customers)") as exp:
    st.markdown("""
    **Description**: Customer profiles ingested from operational databases. Formats names, handles missing emails, and calculates accounts longevity.
    
    - **Primary Key**: `customer_id` (enforced unique)
    - **Staging Schema & Casting Rules**:
      - `customer_id` (STRING)
      - `first_name` (STRING)
      - `last_name` (STRING)
      - `email` (STRING)
      - `country_code` (STRING)
      - `signup_date` (DATE)
      - `days_since_signup` (INT64) - Calculated dynamically
    - **Active Validation Rules**:
      - `customer_id` must be unique.
      - `customer_id`, `email` must not be null.
    """)

with st.expander("📦 order_items (staging.stg_order_items)") as exp:
    st.markdown("""
    **Description**: Fine-grained line items inside each sales order. Integrates product listings with quantities and unit pricing.
    
    - **Primary Key**: `item_id` (enforced unique)
    - **Staging Schema & Casting Rules**:
      - `item_id` (STRING)
      - `order_id` (STRING)
      - `product_id` (STRING)
      - `quantity` (INT64)
      - `unit_price_usd` (NUMERIC)
      - `line_revenue_usd` (NUMERIC) - Calculated dynamically (`quantity * unit_price_usd`)
    - **Active Validation Rules**:
      - `item_id` must be unique.
      - `item_id`, `order_id`, `product_id` must not be null.
    """)

with st.expander("↩️ returns (staging.stg_returns)") as exp:
    st.markdown("""
    **Description**: Track returns, reasons, and refund sums. Surfaces product defect and service issues.
    
    - **Primary Key**: `return_id` (enforced unique)
    - **Staging Schema & Casting Rules**:
      - `return_id` (STRING)
      - `order_id` (STRING)
      - `product_id` (STRING)
      - `return_date` (DATE)
      - `return_reason` (STRING)
      - `refund_amount_usd` (NUMERIC)
    - **Active Validation Rules**:
      - `return_id` must be unique.
      - `return_id`, `order_id` must not be null.
      - *Note: Warning status generated due to simulation of incomplete return reasons in raw files.*
    """)