import sys
import os
import datetime

import streamlit as st
import pandas as pd

# allow imports from utils/ and components/
sys.path.append(os.path.dirname(__file__))

from utils.bq_client import run_query
from utils import queries as q
from utils.churn_model import get_churn_predictions
from components.kpi_cards import render_kpi_cards
from components.charts import (
    revenue_trend_chart,
    channel_bar_chart,
    category_pie_chart,
    segment_bar_chart,
    conversion_funnel_chart,
    returns_bar_chart, 
    margin_by_category_chart,
    marketing_roi_chart, 
    marketing_spend_trend_chart,
)

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
st.sidebar.caption("Data refreshes every 5 minutes.")

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
# ── Products + Categories ────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📈 Overview", "🏆 Products & Margin", "👥 Customers", "↩️ Returns", "📣 Marketing", "🔻 Funnel"]
)

with tab1:
    st.info(
        "The Revenue Trend and Revenue by Channel charts are already displayed "
        "at the top of the dashboard. Use the tabs below for deeper analysis."
    )

with tab2:
    c3, c4 = st.columns([1.3,1])
    with c3:
        st.subheader("Top 20 Products")
        df = run_query(q.TOP_PRODUCTS)
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={
            "revenue": st.column_config.NumberColumn("Revenue", format="$%.0f"),
            "profit": st.column_config.NumberColumn("Profit", format="$%.0f"),
            "margin_pct": st.column_config.NumberColumn("Margin %", format="%.1f%%"),
        })
    with c4:
        df = run_query(q.CATEGORY_BREAKDOWN)
        if not df.empty: category_pie_chart(df)
    st.markdown("---")
    df = run_query(q.MARGIN_BY_CATEGORY)
    if not df.empty: margin_by_category_chart(df)

with tab3:
    c5, c6 = st.columns([1,1])
    seg_df = run_query(q.CUSTOMER_SEGMENTS)
    with c5:
        if not seg_df.empty: segment_bar_chart(seg_df)
    with c6:
        if not seg_df.empty:
            st.dataframe(seg_df, use_container_width=True, hide_index=True, column_config={
                "total_ltv": st.column_config.NumberColumn("Total LTV", format="$%.0f"),
                "avg_ltv": st.column_config.NumberColumn("Avg LTV", format="$%.2f"),
                "avg_orders": st.column_config.NumberColumn("Avg Orders", format="%.1f"),
            })

    st.markdown("---")
    st.subheader("🚨 Churn Risk Prediction")
    st.caption("Logistic Regression model trained on order recency, 30-day frequency, and AOV trend (scikit-learn)")

    with st.spinner("Training churn model on BigQuery data..."):
        churn_df = get_churn_predictions()

    if not churn_df.empty:
        # KPI row
        high_risk = churn_df[churn_df['risk_tier'] == 'High']
        med_risk  = churn_df[churn_df['risk_tier'] == 'Medium']
        low_risk  = churn_df[churn_df['risk_tier'] == 'Low']
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🔴 High Risk",   f"{len(high_risk):,}",  f"{len(high_risk)/len(churn_df)*100:.1f}% of customers")
        k2.metric("🟡 Medium Risk", f"{len(med_risk):,}",   f"{len(med_risk)/len(churn_df)*100:.1f}% of customers")
        k3.metric("🟢 Low Risk",    f"{len(low_risk):,}",   f"{len(low_risk)/len(churn_df)*100:.1f}% of customers")
        k4.metric("💰 At-Risk LTV", f"${high_risk['lifetime_value_usd'].sum():,.0f}")

        st.markdown("")

        # Risk tier distribution bar
        import plotly.express as px
        tier_counts = churn_df['risk_tier'].value_counts().reset_index()
        tier_counts.columns = ['Risk Tier', 'Customers']
        tier_order = ['High', 'Medium', 'Low']
        tier_counts['Risk Tier'] = pd.Categorical(tier_counts['Risk Tier'], categories=tier_order, ordered=True)
        tier_counts = tier_counts.sort_values('Risk Tier')
        color_map = {'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#22c55e'}
        fig_tier = px.bar(
            tier_counts, x='Risk Tier', y='Customers',
            color='Risk Tier', color_discrete_map=color_map,
            title='Customer Churn Risk Distribution',
            text='Customers'
        )
        fig_tier.update_traces(textposition='outside')
        fig_tier.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_tier, use_container_width=True)

        # Top at-risk customers table
        st.subheader("Top 25 High-Risk Customers")
        display_cols = ['full_name', 'email', 'rfm_segment', 'country_code',
                        'days_since_last_order', 'order_frequency_30d',
                        'lifetime_value_usd', 'churn_probability']
        st.dataframe(
            high_risk[display_cols].head(25).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            column_config={
                "full_name":             st.column_config.TextColumn("Name"),
                "email":                 st.column_config.TextColumn("Email"),
                "rfm_segment":           st.column_config.TextColumn("RFM Segment"),
                "country_code":          st.column_config.TextColumn("Country"),
                "days_since_last_order": st.column_config.NumberColumn("Days Since Order", format="%d"),
                "order_frequency_30d":   st.column_config.NumberColumn("Orders (30d)", format="%d"),
                "lifetime_value_usd":    st.column_config.NumberColumn("LTV", format="$%.0f"),
                "churn_probability":     st.column_config.ProgressColumn(
                    "Churn Risk", format="%.0f%%", min_value=0, max_value=1
                ),
            }
        )
    else:
        st.warning("Churn model could not be loaded. Check BigQuery connectivity.")

with tab4:
    ret_df = run_query(q.RETURNS_SUMMARY)
    if not ret_df.empty:
        r = ret_df.iloc[0]
        r1, r2, r3 = st.columns(3)
        r1.metric("Total Returns", f"{int(r['total_returns']):,}" if pd.notna(r['total_returns']) else "0")
        r2.metric("Total Refunded", f"${r['total_refunded']:,.0f}" if pd.notna(r['total_refunded']) else "$0")
        r3.metric("Avg Return Rate", f"{r['avg_return_rate']:.1f}%" if pd.notna(r['avg_return_rate']) else "0%")
    st.markdown("---")
    df = run_query(q.TOP_RETURNED_PRODUCTS)
    if not df.empty:
        returns_bar_chart(df)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No return data.")

with tab5:
    roi_df = run_query(q.MARKETING_ROI.format(start=start_date,end=end_date))
    if not roi_df.empty:
        c7, c8 = st.columns([1,1])
        with c7: marketing_roi_chart(roi_df)
        with c8:
            st.dataframe(roi_df, use_container_width=True, hide_index=True, column_config={
                "total_spend": st.column_config.NumberColumn("Spend", format="$%.0f"),
                "total_revenue": st.column_config.NumberColumn("Revenue", format="$%.0f"),
                "avg_roas": st.column_config.NumberColumn("ROAS", format="%.2f"),
                "avg_ctr": st.column_config.NumberColumn("CTR %", format="%.2f%%"),
            })
        st.markdown("---")
        df = run_query(q.MARKETING_TREND.format(start=start_date,end=end_date))
        if not df.empty: marketing_spend_trend_chart(df)
    else:
        st.info("No marketing data for this period.")

with tab6:
    funnel_df = run_query(q.CONVERSION_FUNNEL.format(start=start_date,end=end_date))
    if not funnel_df.empty and funnel_df.iloc[0]["sessions"]:
        conversion_funnel_chart(funnel_df)
    else:
        st.info("No funnel data for this period.")

st.markdown("---")
st.caption("Phase 1 + Phase 2 complete: Analytics Foundation · BigQuery + dbt + Streamlit + Gemini AI Copilot")