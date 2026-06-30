import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = px.colors.qualitative.Set2


def revenue_trend_chart(df: pd.DataFrame, granularity: str = "Daily"):
    """Line chart of revenue over time."""
    if granularity == "Weekly":
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])
        df = df.resample("W", on="order_date").sum().reset_index()
    elif granularity == "Monthly":
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])
        df = df.resample("ME", on="order_date").sum().reset_index()

    fig = px.line(
        df, x="order_date", y="revenue",
        title=f"{granularity} Revenue",
        labels={"order_date": "Date", "revenue": "Revenue (USD)"},
        color_discrete_sequence=["#636EFA"]
    )
    fig.update_layout(hovermode="x unified", height=350)
    st.plotly_chart(fig, use_container_width=True)


def channel_bar_chart(df: pd.DataFrame):
    """Horizontal bar chart of revenue by channel."""
    fig = px.bar(
        df.sort_values("revenue"),
        x="revenue", y="channel_name",
        orientation="h",
        title="Revenue by Channel",
        labels={"revenue": "Revenue (USD)", "channel_name": "Channel"},
        color="channel_name",
        color_discrete_sequence=PALETTE
    )
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)


def category_pie_chart(df: pd.DataFrame):
    """Pie chart of revenue by product category."""
    fig = px.pie(
        df, values="revenue", names="category",
        title="Revenue by Category",
        color_discrete_sequence=PALETTE,
        hole=0.4
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


def segment_bar_chart(df: pd.DataFrame):
    """Bar chart of customer count by RFM segment."""
    fig = px.bar(
        df.sort_values("customers", ascending=False),
        x="rfm_segment", y="customers",
        title="Customers by RFM Segment",
        color="rfm_segment",
        color_discrete_sequence=PALETTE,
        labels={"rfm_segment": "Segment", "customers": "# Customers"}
    )
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)


def conversion_funnel_chart(df: pd.DataFrame):
    """Funnel chart: sessions → views → cart → purchase."""
    row = df.iloc[0]
    stages = ["Sessions", "Product Views", "Add to Cart", "Purchases"]
    values = [row["sessions"], row["product_views"], row["add_to_cart"], row["purchases"]]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker=dict(color=["#636EFA", "#EF553B", "#00CC96", "#AB63FA"])
    ))
    fig.update_layout(title="Conversion Funnel", height=350)
    st.plotly_chart(fig, use_container_width=True)