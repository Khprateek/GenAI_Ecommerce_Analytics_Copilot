import os

PROJECT = os.environ.get("GCP_PROJECT_ID", "your-project")
METRICS = f"`{PROJECT}.metrics`"
MARTS   = f"`{PROJECT}.marts`"
STAGING = f"`{PROJECT}.staging`"


# ── MONTHLY DASHBOARD METRICS ─────────────────────────────────────────────────
MONTHLY_KPI_SUMMARY = f"""
SELECT
    SUM(net_revenue_usd) AS month_revenue,
    SUM(total_orders) AS month_orders,
    AVG(avg_order_value_usd) AS month_aov,
    SUM(unique_customers) AS month_customers,
    SUM(total_items_sold) AS month_items_sold
FROM {METRICS}.revenue_daily
WHERE order_year = EXTRACT(YEAR FROM DATE('{{date}}'))
  AND order_month = EXTRACT(MONTH FROM DATE('{{date}}'))
"""

# ── BUSINESS KPIs (OVERVIEW) ───────────────────────────────────────────────────
BUSINESS_KPI_SUMMARY = f"""
WITH revenue AS (
    SELECT
        SUM(gross_revenue_usd) AS gmv,
        SUM(net_revenue_usd) AS net_revenue,
        SUM(total_discounts_usd) AS total_discounts,
        SUM(total_orders) AS total_orders,
        SUM(cancelled_orders) AS cancelled_orders
    FROM {METRICS}.revenue_daily
    WHERE order_date BETWEEN DATE('{{start}}') AND DATE('{{end}}')
)
SELECT
    gmv,
    net_revenue,
    total_discounts / NULLIF(gmv, 0) AS discount_drag_rate,
    (total_orders - cancelled_orders) / NULLIF(total_orders, 0) AS order_fulfillment_rate
FROM revenue
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

# ── MARGIN BY CATEGORY ─────────────────────────────────────────────────────────
MARGIN_BY_CATEGORY = f"""
select
    category,
    round(avg(margin_pct), 1)           as avg_margin_pct,
    sum(gross_profit_usd)               as total_profit,
    sum(total_revenue_usd)              as total_revenue
from {METRICS}.product_performance
group by category
order by avg_margin_pct desc
"""

# ── RETURNS ────────────────────────────────────────────────────────────────────
RETURNS_SUMMARY = f"""
with returns as (
    select * from {STAGING}.stg_returns
),
completed_orders as (
    select count(distinct order_id) as order_count
    from {MARTS}.fact_orders
    where is_completed = 1
)
select
    count(distinct r.return_id)                             as total_returns,
    sum(r.refund_amount_usd)                                as total_refunded,
    round(safe_divide(
        count(distinct r.return_id),
        (select order_count from completed_orders)
    ) * 100, 2)                                             as avg_return_rate
from returns r
"""

TOP_RETURNED_PRODUCTS = f"""
select
    p.product_name,
    p.category,
    count(*)                        as return_count,
    sum(r.refund_amount_usd)        as total_refunded
from {STAGING}.stg_returns r
inner join {MARTS}.dim_products p on r.product_id = p.product_id
group by p.product_name, p.category
order by return_count desc
limit 15
"""

# ── MARKETING ──────────────────────────────────────────────────────────────────
MARKETING_ROI = f"""
select
    channel,
    sum(spend_usd)                  as total_spend,
    sum(attributed_revenue_usd)     as total_revenue,
    round(avg(roas), 2)             as avg_roas,
    round(avg(ctr_pct), 2)            as avg_ctr
from {METRICS}.marketing_performance
where spend_date between date('{{start}}') and date('{{end}}')
group by channel
order by total_revenue desc
"""

MARKETING_TREND = f"""
select
    spend_date,
    sum(spend_usd)                  as spend,
    sum(attributed_revenue_usd)     as revenue
from {METRICS}.marketing_performance
where spend_date between date('{{start}}') and date('{{end}}')
group by spend_date
order by spend_date
"""