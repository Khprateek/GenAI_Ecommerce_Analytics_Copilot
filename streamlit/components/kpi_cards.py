import streamlit as st
import pandas as pd

def render_kpi_cards(df: pd.DataFrame):
    """Renders 4 KPI metric cards in a row."""
    row = df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=f"${row['total_revenue']:,.0f}",
        )
    with col2:
        st.metric(
            label="🛒 Total Orders",
            value=f"{int(row['total_orders']):,}",
        )
    with col3:
        st.metric(
            label="🧾 Avg Order Value",
            value=f"${row['avg_order_value']:,.2f}",
        )
    with col4:
        st.metric(
            label="👥 Unique Customers",
            value=f"{int(row['unique_customers']):,}",
        )