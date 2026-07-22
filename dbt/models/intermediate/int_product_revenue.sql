-- ============================================================================
-- int_product_revenue.sql
-- ============================================================================
-- Aggregates product-level revenue, profitability, and quality metrics.
-- Quick-commerce specific: includes substitution rates, issue rates per
-- product, and perishable-goods analysis.
--
-- Grain: one row per product_id
-- Depends on: stg_order_items, stg_orders, stg_products, stg_order_issues
-- ============================================================================

with items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select order_id, order_date, order_status
    from {{ ref('stg_orders') }}
    where order_status = 'DELIVERED'
),

products as (
    select * from {{ ref('stg_products') }}
),

-- ── Issues at the product level ─────────────────────────────────────────────
product_issues as (
    select
        product_id,
        count(issue_id)             as total_issues,
        sum(refund_amount)          as total_refund_amount,
        approx_top_count(issue_type, 1)[offset(0)].value
                                    as top_issue_type
    from {{ ref('stg_order_issues') }}
    group by product_id
),

-- ── Item-level join (only delivered orders) ─────────────────────────────────
delivered_items as (
    select
        i.item_id,
        i.order_id,
        i.product_id,
        i.quantity,
        i.unit_price,
        i.line_revenue,
        i.is_substituted,
        o.order_date
    from items i
    inner join orders o on i.order_id = o.order_id
),

-- ── Aggregate at product level ──────────────────────────────────────────────
product_revenue as (
    select
        di.product_id,

        -- Volume
        count(distinct di.order_id)                 as total_orders,
        sum(di.quantity)                             as total_units_sold,
        count(distinct di.item_id)                  as total_line_items,

        -- Revenue (INR)
        round(sum(di.line_revenue), 2)              as total_revenue,
        round(avg(di.unit_price), 2)                as avg_selling_price,

        -- Substitution
        countif(di.is_substituted)                  as substitution_count,
        round(safe_divide(
            countif(di.is_substituted),
            count(distinct di.item_id)
        ) * 100, 2)                                 as substitution_rate_pct,

        -- Time range
        min(di.order_date)                          as first_sold_date,
        max(di.order_date)                          as last_sold_date,
        date_diff(max(di.order_date), min(di.order_date), day)
                                                    as selling_span_days

    from delivered_items di
    group by di.product_id
)

-- ── Final output: enrich with product attributes & profitability ────────────
select
    pr.product_id,

    -- Product details
    p.product_name,
    p.category_name,
    p.brand_name,
    p.pack_size,
    p.is_perishable,
    p.shelf_life_days,

    -- Pricing
    p.mrp,
    p.selling_price,
    p.cost_price,
    round(safe_divide(p.mrp - p.selling_price, p.mrp) * 100, 2)
                                                    as discount_from_mrp_pct,
    round(safe_divide(p.selling_price - p.cost_price, p.selling_price) * 100, 2)
                                                    as gross_margin_pct,

    -- Volume
    pr.total_orders,
    pr.total_units_sold,

    -- Revenue & Profit (INR)
    pr.total_revenue,
    pr.avg_selling_price,
    round(pr.total_revenue - (pr.total_units_sold * p.cost_price), 2)
                                                    as gross_profit,
    round(
        safe_divide(
            pr.total_revenue - (pr.total_units_sold * p.cost_price),
            pr.total_revenue
        ) * 100,
        2
    )                                               as realised_margin_pct,

    -- Substitution
    pr.substitution_count,
    pr.substitution_rate_pct,

    -- Quality / Issues
    coalesce(pi.total_issues, 0)                    as total_issues,
    coalesce(pi.total_refund_amount, 0)             as total_refund_amount,
    round(safe_divide(
        coalesce(pi.total_issues, 0),
        nullif(pr.total_orders, 0)
    ) * 100, 2)                                     as issue_rate_pct,
    pi.top_issue_type,

    -- Velocity
    pr.first_sold_date,
    pr.last_sold_date,
    pr.selling_span_days,
    round(safe_divide(pr.total_units_sold,
          nullif(pr.selling_span_days, 0)), 2)      as units_per_day

from product_revenue pr
left join products       p  on pr.product_id = p.product_id
left join product_issues pi on pr.product_id = pi.product_id
