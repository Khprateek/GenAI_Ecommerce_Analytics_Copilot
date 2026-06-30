import sys
import os
import datetime

import streamlit as st
import pandas as pd

# allow imports from utils/ and components/
sys.path.append(os.path.dirname(__file__))

from utils.bq_client import run_query
from utils import queries as q
from components.kpi_cards import render_kpi_cards
from components.charts import (
    revenue_trend_chart,
    channel_bar_chart,
    category_pie_chart,
    segment_bar_chart,
    conversion_funnel_chart,
)

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 E-Commerce Analytics Dashboard")
st.caption("Phase 1 — Analytics Foundation · BigQuery + dbt + Streamlit")

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.header("Filters")

default_end = datetime.date.today()
default_start = default_end - datetime.timedelta(days=90)

date_range = st.sidebar.date_input(
    "Date range",
    value=(default_start, default_end),
)

if len(date_range) != 2:
    st.stop()

start_date, end_date = date_range

granularity = st.sidebar.selectbox("Revenue trend granularity", ["Daily", "Weekly", "Monthly"])

st.sidebar.markdown("---")
st.sidebar.caption("Data refreshes every 5 minutes (cached).")

# ── KPI Row ───────────────────────────────────────────────────────────────────
kpi_sql = q.KPI_SUMMARY.format(start=start_date, end=end_date)
kpi_df = run_query(kpi_sql)

if kpi_df.empty or kpi_df.iloc[0]["total_revenue"] is None:
    st.warning("No data found for the selected date range.")
else:
    render_kpi_cards(kpi_df)

st.markdown("---")

# ── Revenue Trend + Channel ──────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    trend_sql = q.REVENUE_TREND.format(start=start_date, end=end_date)
    trend_df = run_query(trend_sql)
    if not trend_df.empty:
        revenue_trend_chart(trend_df, granularity)
    else:
        st.info("No revenue trend data for this period.")

with col2:
    channel_sql = q.REVENUE_BY_CHANNEL.format(start=start_date, end=end_date)
    channel_df = run_query(channel_sql)
    if not channel_df.empty:
        channel_bar_chart(channel_df)
    else:
        st.info("No channel data for this period.")

st.markdown("---")

# ── Products + Categories ────────────────────────────────────────────────────
col3, col4 = st.columns([1.3, 1])

with col3:
    st.subheader("🏆 Top 20 Products")
    products_df = run_query(q.TOP_PRODUCTS)
    st.dataframe(
        products_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "revenue": st.column_config.NumberColumn("Revenue", format="$%.0f"),
            "margin_pct": st.column_config.NumberColumn("Margin %", format="%.1f%%"),
        }
    )

with col4:
    category_df = run_query(q.CATEGORY_BREAKDOWN)
    if not category_df.empty:
        category_pie_chart(category_df)

st.markdown("---")

# ── Customer Segments ────────────────────────────────────────────────────────
st.subheader("👥 Customer Segments (RFM)")
col5, col6 = st.columns([1, 1])

with col5:
    segments_df = run_query(q.CUSTOMER_SEGMENTS)
    if not segments_df.empty:
        segment_bar_chart(segments_df)

with col6:
    if not segments_df.empty:
        st.dataframe(
            segments_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "total_ltv": st.column_config.NumberColumn("Total LTV", format="$%.0f"),
                "avg_ltv": st.column_config.NumberColumn("Avg LTV", format="$%.2f"),
                "avg_orders": st.column_config.NumberColumn("Avg Orders", format="%.1f"),
            }
        )

st.markdown("---")

# ── Conversion Funnel ────────────────────────────────────────────────────────
st.subheader("🔻 Conversion Funnel")
funnel_sql = q.CONVERSION_FUNNEL.format(start=start_date, end=end_date)
funnel_df = run_query(funnel_sql)

if not funnel_df.empty and funnel_df.iloc[0]["sessions"]:
    conversion_funnel_chart(funnel_df)
else:
    st.info("No event/funnel data for this period.")

st.markdown("---")
st.caption("Phase 2 will add: Gemini-powered natural-language SQL querying and AI-generated insights.")