import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = px.colors.qualitative.Set2


def revenue_trend_chart(df: pd.DataFrame, granularity: str = "Daily", key="revenue_trend"):
    """Line chart of revenue over time."""
    if "revenue" in df.columns:
        df["revenue"] = df["revenue"].astype(float)
    if "orders" in df.columns:
        df["orders"] = df["orders"].astype(float)

    if granularity == "Weekly":
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])
        df = df.resample("W", on="order_date").sum(numeric_only=True).reset_index()

    elif granularity == "Monthly":
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])
        df = df.resample("ME", on="order_date").sum(numeric_only=True).reset_index()

    fig = px.line(
        df,
        x="order_date",
        y="revenue",
        title=f"{granularity} Revenue",
        labels={"order_date": "Date", "revenue": "Revenue (INR)"},
        color_discrete_sequence=["#636EFA"],
    )

    fig.update_layout(
        hovermode="x unified",
        height=350,
    )

    st.plotly_chart(fig, use_container_width=True, key=key)


def platform_bar_chart(df: pd.DataFrame, key="platform_bar"):
    """Horizontal bar chart of revenue by platform."""

    fig = px.bar(
        df.sort_values("revenue"),
        x="revenue",
        y="platform",
        orientation="h",
        title="Revenue by Platform",
        labels={
            "revenue": "Revenue (INR)",
            "platform": "Platform",
        },
        color="platform",
        color_discrete_sequence=PALETTE,
    )

    fig.update_layout(showlegend=False, height=300)

    st.plotly_chart(fig, use_container_width=True, key=key)


def category_pie_chart(df: pd.DataFrame, key="category_pie"):
    """Pie chart of revenue by product category."""

    fig = px.pie(
        df,
        values="revenue",
        names="category",
        title="Revenue by Category",
        color_discrete_sequence=PALETTE,
        hole=0.4,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=350)

    st.plotly_chart(fig, use_container_width=True, key=key)


def segment_bar_chart(df: pd.DataFrame, key="segment_bar"):
    """Bar chart of customer count by RFM segment."""

    fig = px.bar(
        df.sort_values("customers", ascending=False),
        x="rfm_segment",
        y="customers",
        title="Customers by RFM Segment",
        color="rfm_segment",
        color_discrete_sequence=PALETTE,
        labels={
            "rfm_segment": "Segment",
            "customers": "# Customers",
        },
    )

    fig.update_layout(showlegend=False, height=350)

    st.plotly_chart(fig, use_container_width=True, key=key)


def conversion_funnel_chart(df: pd.DataFrame, key="conversion_funnel"):
    """Funnel chart dynamically generated from funnel_stages data."""

    fig = go.Figure(
        go.Funnel(
            y=df["stage_name"].tolist(),
            x=df["user_count"].tolist(),
            textinfo="value+percent initial",
            marker=dict(
                color=[
                    "#636EFA",
                    "#EF553B",
                    "#00CC96",
                    "#AB63FA",
                ][:len(df)]
            ),
        )
    )

    fig.update_layout(
        title="Conversion Funnel",
        height=350,
    )

    st.plotly_chart(fig, use_container_width=True, key=key)


def issues_bar_chart(df: pd.DataFrame, key="issues_bar"):
    """Top products with issues."""

    fig = px.bar(
        df.sort_values("total_issues"),
        x="total_issues",
        y="product_name",
        orientation="h",
        title="Top Products with Issues",
        labels={
            "total_issues": "# Issues",
            "product_name": "Product",
        },
        color="total_issues",
        color_continuous_scale="Reds",
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        coloraxis_showscale=False,
    )

    st.plotly_chart(fig, use_container_width=True, key=key)


def margin_by_category_chart(df: pd.DataFrame, key="margin_category"):
    """Average margin by category."""

    fig = px.bar(
        df.sort_values("avg_margin_pct", ascending=False),
        x="category",
        y="avg_margin_pct",
        title="Average Realised Margin by Category",
        labels={
            "category": "Category",
            "avg_margin_pct": "Avg Margin (%)",
        },
        color="category",
        color_discrete_sequence=PALETTE,
    )

    fig.update_layout(
        showlegend=False,
        height=350,
    )

    st.plotly_chart(fig, use_container_width=True, key=key)


def marketing_roi_chart(df: pd.DataFrame, key="marketing_roi"):
    """Marketing spend vs attributed revenue."""

    plot_df = df.melt(
        id_vars=["channel"],
        value_vars=[
            "total_spend",
            "total_revenue",
        ],
        var_name="metric",
        value_name="amount",
    )

    plot_df["metric"] = plot_df["metric"].replace(
        {
            "total_spend": "Spend",
            "total_revenue": "Revenue",
        }
    )

    fig = px.bar(
        plot_df,
        x="channel",
        y="amount",
        color="metric",
        barmode="group",
        title="Marketing Spend vs Attributed Revenue",
        labels={
            "channel": "Channel",
            "amount": "INR",
            "metric": "",
        },
        color_discrete_sequence=["#EF553B", "#00CC96"],
    )

    fig.update_layout(height=350)

    st.plotly_chart(fig, use_container_width=True, key=key)


def marketing_spend_trend_chart(df: pd.DataFrame, key="marketing_spend_trend"):
    """Daily marketing spend vs revenue."""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["spend_date"],
            y=df["spend"],
            mode="lines",
            name="Spend",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["spend_date"],
            y=df["revenue"],
            mode="lines",
            name="Revenue",
        )
    )

    fig.update_layout(
        title="Marketing Spend vs Revenue Trend",
        xaxis_title="Date",
        yaxis_title="INR",
        hovermode="x unified",
        height=350,
    )

    st.plotly_chart(fig, use_container_width=True, key=key)