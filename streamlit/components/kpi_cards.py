import streamlit as st
import pandas as pd

def render_monthly_kpi_cards(df: pd.DataFrame):
    """Renders 5 Monthly KPI metric cards in a row."""
    row = df.iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="💰 Monthly Revenue",
            value=f"${row['month_revenue']:,.0f}" if pd.notna(row['month_revenue']) else "$0",
        )
    with col2:
        st.metric(
            label="🛒 Monthly Orders",
            value=f"{int(row['month_orders']):,}" if pd.notna(row['month_orders']) else "0",
        )
    with col3:
        st.metric(
            label="🧾 Monthly Avg Order Value",
            value=f"${row['month_aov']:,.2f}" if pd.notna(row['month_aov']) else "$0.00",
        )
    with col4:
        st.metric(
            label="👥 Monthly New Customers",
            value=f"{int(row['month_customers']):,}" if pd.notna(row['month_customers']) else "0",
        )
    with col5:
        st.metric(
            label="📦 Monthly Items Sold",
            value=f"{int(row['month_items_sold']):,}" if pd.notna(row['month_items_sold']) else "0",
        )

def render_business_kpi_cards(df: pd.DataFrame):
    """Renders 4 Business KPI metric cards in a row."""
    row = df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📈 Gross Merchandise Value (GMV)",
            value=f"${row['gmv']:,.0f}" if pd.notna(row['gmv']) else "$0",
        )
    with col2:
        st.metric(
            label="💵 Net Revenue",
            value=f"${row['net_revenue']:,.0f}" if pd.notna(row['net_revenue']) else "$0",
        )
    with col3:
        discount_drag = row['discount_drag_rate']
        st.metric(
            label="📉 Discount Drag Rate",
            value=f"{discount_drag * 100:.2f}%" if pd.notna(discount_drag) else "0.00%",
        )
    with col4:
        fulfillment = row['order_fulfillment_rate']
        st.metric(
            label="🚚 Order Fulfillment Rate",
            value=f"{fulfillment * 100:.2f}%" if pd.notna(fulfillment) else "0.00%",
        )