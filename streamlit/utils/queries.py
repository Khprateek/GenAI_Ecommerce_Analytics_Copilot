import os

PROJECT = os.environ.get("GCP_PROJECT_ID", "your-project")
METRICS = f"`{PROJECT}.metrics`"
MARTS   = f"`{PROJECT}.marts`"


# ── KPI SUMMARY ────────────────────────────────────────────────────────────────
KPI_SUMMARY = f"""
select
    sum(gross_revenue_usd)              as total_revenue,
    sum(total_orders)                   as total_orders,
    avg(avg_order_value_usd)            as avg_order_value,
    count(distinct unique_customers)    as unique_customers
from {METRICS}.revenue_daily
where order_date between date('{{start}}') and date('{{end}}')
"""

# ── REVENUE TREND ──────────────────────────────────────────────────────────────
REVENUE_TREND = f"""
select
    order_date,
    sum(gross_revenue_usd)  as revenue,
    sum(total_orders)       as orders
from {METRICS}.revenue_daily
where order_date between date('{{start}}') and date('{{end}}')
group by order_date
order by order_date
"""

# ── REVENUE BY CHANNEL ─────────────────────────────────────────────────────────
REVENUE_BY_CHANNEL = f"""
select
    channel_name,
    sum(gross_revenue_usd)  as revenue,
    sum(total_orders)       as orders
from {METRICS}.revenue_daily
where order_date between date('{{start}}') and date('{{end}}')
group by channel_name
order by revenue desc
"""

# ── TOP PRODUCTS ───────────────────────────────────────────────────────────────
TOP_PRODUCTS = f"""
select
    product_name,
    category,
    brand,
    total_revenue_usd   as revenue,
    total_units_sold    as units,
    margin_pct,
    sales_performance
from {METRICS}.product_performance
order by revenue desc
limit 20
"""

# ── CATEGORY BREAKDOWN ─────────────────────────────────────────────────────────
CATEGORY_BREAKDOWN = f"""
select
    category,
    sum(total_revenue_usd)  as revenue,
    sum(total_units_sold)   as units
from {METRICS}.product_performance
group by category
order by revenue desc
"""

# ── CUSTOMER SEGMENTS ──────────────────────────────────────────────────────────
CUSTOMER_SEGMENTS = f"""
select
    rfm_segment,
    count(*)                    as customers,
    sum(lifetime_value_usd)     as total_ltv,
    avg(lifetime_value_usd)     as avg_ltv,
    avg(total_orders)           as avg_orders
from {METRICS}.customer_ltv
group by rfm_segment
order by total_ltv desc
"""

# ── VALUE TIERS ────────────────────────────────────────────────────────────────
VALUE_TIERS = f"""
select
    value_tier,
    count(*) as customers,
    avg(lifetime_value_usd) as avg_ltv
from {METRICS}.customer_ltv
group by value_tier
"""

# ── CONVERSION FUNNEL ──────────────────────────────────────────────────────────
CONVERSION_FUNNEL = f"""
select
    sum(sessions)       as sessions,
    sum(product_views)  as product_views,
    sum(add_to_cart)    as add_to_cart,
    sum(purchases)      as purchases
from {METRICS}.conversion_rate
where event_date between date('{{start}}') and date('{{end}}')
"""

# ── DAILY CONVERSION TREND ─────────────────────────────────────────────────────
CONVERSION_TREND = f"""
select
    event_date,
    avg(purchase_rate_pct) as conversion_rate
from {METRICS}.conversion_rate
where event_date between date('{{start}}') and date('{{end}}')
group by event_date
order by event_date
"""