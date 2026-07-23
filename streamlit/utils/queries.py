import os

PROJECT = os.environ.get("GCP_PROJECT_ID", "your-project")
METRICS = f"`{PROJECT}.metrics`"
MARTS   = f"`{PROJECT}.marts`"
STAGING = f"`{PROJECT}.staging`"


# ── MONTHLY DASHBOARD METRICS ─────────────────────────────────────────────────
MONTHLY_KPI_SUMMARY = f"""
SELECT
    SUM(net_revenue) AS month_revenue,
    SUM(total_orders) AS month_orders,
    SAFE_DIVIDE(SUM(net_revenue), SUM(total_orders)) AS month_aov,
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
        SUM(gross_revenue) AS gmv,
        SUM(net_revenue) AS net_revenue,
        SUM(total_discount) AS total_discounts,
        SUM(total_orders) AS total_orders,
        SUM(cancelled_orders) AS cancelled_orders,
        SUM(delivered_orders) AS delivered_orders,
        AVG(avg_delivery_minutes) AS avg_delivery_minutes,
        AVG(on_time_pct) AS on_time_pct,
        SAFE_DIVIDE(SUM(delivered_orders), SUM(total_orders)) AS fulfilment_rate_pct
    FROM {METRICS}.revenue_daily
    WHERE order_date BETWEEN DATE('{{start}}') AND DATE('{{end}}')
)
SELECT
    gmv,
    net_revenue,
    total_discounts / NULLIF(gmv, 0) AS discount_drag_rate,
    fulfilment_rate_pct,
    avg_delivery_minutes,
    on_time_pct
FROM revenue
"""

# ── REVENUE TREND ──────────────────────────────────────────────────────────────
REVENUE_TREND = f"""
select
    order_date,
    sum(gross_revenue)  as revenue,
    sum(total_orders)   as orders
from {METRICS}.revenue_daily
where order_date between date('{{start}}') and date('{{end}}')
group by order_date
order by order_date
"""

# ── REVENUE BY PLATFORM ─────────────────────────────────────────────────────────
REVENUE_BY_PLATFORM = f"""
select
    platform,
    sum(gross_revenue)  as revenue,
    sum(total_orders)       as orders
from {METRICS}.revenue_daily
where order_date between date('{{start}}') and date('{{end}}')
group by platform
order by revenue desc
"""

# ── TOP PRODUCTS ───────────────────────────────────────────────────────────────
TOP_PRODUCTS = f"""
select
    product_name,
    category_name,
    brand_name,
    total_revenue       as revenue,
    total_units_sold    as units,
    realised_margin_pct as margin_pct,
    sales_performance
from {METRICS}.product_performance
order by revenue desc
limit 20
"""

# ── CATEGORY BREAKDOWN ─────────────────────────────────────────────────────────
CATEGORY_BREAKDOWN = f"""
select
    category_name as category,
    sum(total_revenue)  as revenue,
    sum(total_units_sold)   as units
from {METRICS}.product_performance
group by category_name
order by revenue desc
"""

# ── CUSTOMER SEGMENTS ──────────────────────────────────────────────────────────
CUSTOMER_SEGMENTS = f"""
select
    rfm_segment,
    count(*)                    as customers,
    sum(lifetime_revenue)       as total_ltv,
    avg(lifetime_revenue)       as avg_ltv,
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
    avg(lifetime_revenue) as avg_ltv
from {METRICS}.customer_ltv
group by value_tier
"""

# ── CONVERSION FUNNEL ──────────────────────────────────────────────────────────
CONVERSION_FUNNEL = f"""
select
    stage_name,
    sum(user_count) as user_count,
    stage_order
from {METRICS}.funnel_stages
where event_date between date('{{start}}') and date('{{end}}')
group by stage_name, stage_order
order by stage_order
"""

# ── DAILY CONVERSION TREND ─────────────────────────────────────────────────────
CONVERSION_TREND = f"""
select
    event_date,
    avg(view_to_purchase_pct) as conversion_rate
from {METRICS}.conversion_rate
where event_date between date('{{start}}') and date('{{end}}')
group by event_date
order by event_date
"""

# ── MARGIN BY CATEGORY ─────────────────────────────────────────────────────────
MARGIN_BY_CATEGORY = f"""
select
    category_name as category,
    round(avg(realised_margin_pct), 1)  as avg_margin_pct,
    sum(gross_profit)                   as total_profit,
    sum(total_revenue)                  as total_revenue
from {METRICS}.product_performance
group by category_name
order by avg_margin_pct desc
"""

# ── ISSUES & QUALITY (Replaces Returns) ─────────────────────────────────────────
ISSUES_SUMMARY = f"""
SELECT
    SUM(orders_with_issues) AS total_orders_with_issues,
    SUM(total_issues) AS total_issues_count,
    SUM(total_refunds) AS total_refunded_inr,
    ROUND(SAFE_DIVIDE(SUM(orders_with_issues), SUM(delivered_orders)) * 100, 2) AS avg_issue_rate_pct
FROM {METRICS}.revenue_daily
WHERE order_date BETWEEN DATE('{{start}}') AND DATE('{{end}}')
"""

TOP_ISSUED_PRODUCTS = f"""
select
    product_name,
    category_name as category,
    total_issues,
    substitution_count,
    issue_rate_pct
from {METRICS}.product_performance
order by total_issues desc
limit 15
"""

# ── MARKETING ──────────────────────────────────────────────────────────────────
MARKETING_ROI = f"""
select
    channel,
    sum(spend_inr)                  as total_spend,
    sum(attributed_revenue)         as total_revenue,
    round(avg(roas), 2)             as avg_roas,
    round(avg(ctr_pct), 2)          as avg_ctr
from {METRICS}.marketing_performance
where spend_date between date('{{start}}') and date('{{end}}')
group by channel
order by total_revenue desc
"""

MARKETING_TREND = f"""
select
    spend_date,
    sum(spend_inr)                  as spend,
    sum(attributed_revenue)         as revenue
from {METRICS}.marketing_performance
where spend_date between date('{{start}}') and date('{{end}}')
group by spend_date
order by spend_date
"""