import streamlit as st
import pandas as pd

def render_monthly_kpi_cards(df: pd.DataFrame):
    """Renders 5 Monthly KPI metric cards in a row."""
    row = df.iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="💰 Monthly Revenue",
            value=f"₹{row['month_revenue']:,.0f}" if pd.notna(row['month_revenue']) else "₹0",
        )
    with col2:
        st.metric(
            label="🛒 Monthly Orders",
            value=f"{int(row['month_orders']):,}" if pd.notna(row['month_orders']) else "0",
        )
    with col3:
        st.metric(
            label="🧾 Monthly Avg Order Value",
            value=f"₹{row['month_aov']:,.2f}" if pd.notna(row['month_aov']) else "₹0.00",
        )
    with col4:
        st.metric(
            label="👥 Monthly Unique Customers",
            value=f"{int(row['month_customers']):,}" if pd.notna(row['month_customers']) else "0",
        )
    with col5:
        st.metric(
            label="📦 Monthly Items Sold",
            value=f"{int(row['month_items_sold']):,}" if pd.notna(row['month_items_sold']) else "0",
        )

def render_business_kpi_cards(df: pd.DataFrame):
    """Renders 6 Business KPI metric cards for Quick-Commerce."""
    row = df.iloc[0]

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.metric(
            label="📈 Gross Revenue (GMV)",
            value=f"₹{row['gmv']:,.0f}" if pd.notna(row['gmv']) else "₹0",
        )
    with c2:
        st.metric(
            label="💵 Net Revenue",
            value=f"₹{row['net_revenue']:,.0f}" if pd.notna(row['net_revenue']) else "₹0",
        )
    with c3:
        discount_drag = row['discount_drag_rate']
        st.metric(
            label="📉 Discount Drag Rate",
            value=f"{discount_drag * 100:.2f}%" if pd.notna(discount_drag) else "0.00%",
        )
    with c4:
        st.metric(
            label="🚚 Fulfilment Rate",
            value=f"{row['fulfilment_rate_pct']:.1f}%" if pd.notna(row['fulfilment_rate_pct']) else "0%",
        )
    with c5:
        st.metric(
            label="⏱️ Avg Delivery Time",
            value=f"{row['avg_delivery_minutes']:.1f} min" if pd.notna(row['avg_delivery_minutes']) else "0 min",
        )
    with c6:
        st.metric(
            label="✅ On-Time Delivery",
            value=f"{row['on_time_pct']:.1f}%" if pd.notna(row['on_time_pct']) else "0%",
        )