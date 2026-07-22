-- ============================================================================
-- int_customer_orders.sql
-- ============================================================================
-- Customer-level purchase history with RFM scoring & business segmentation.
-- Quick-commerce specific: includes delivery experience, pass-membership
-- impact, and basket behaviour.
--
-- Grain: one row per customer_id
-- Depends on: stg_orders, stg_customers, stg_order_issues
-- ============================================================================

with delivered_orders as (
    select * from {{ ref('stg_orders') }}
    where order_status = 'DELIVERED'
),

all_orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select
        customer_id,
        city_name,
        state_name,
        home_store_id,
        is_pass_member,
        signup_date,
        days_since_signup
    from {{ ref('stg_customers') }}
),

issues as (
    select
        order_id,
        count(issue_id)     as issue_count,
        sum(refund_amount)  as refund_amount
    from {{ ref('stg_order_issues') }}
    group by order_id
),

-- ── Core order-level metrics (delivered only) ───────────────────────────────
customer_stats as (
    select
        o.customer_id,

        -- Recency
        date_diff(current_date(), max(o.order_date), day)   as days_since_last_order,

        -- Frequency
        count(distinct o.order_id)                          as total_orders,

        -- Monetary (INR)
        round(sum(o.revenue), 2)                            as lifetime_revenue,
        round(avg(o.revenue), 2)                            as avg_order_value,
        round(sum(o.revenue + coalesce(o.delivery_fee, 0)
                  - coalesce(o.discount, 0)
                  - coalesce(i.refund_amount, 0)), 2)       as lifetime_net_revenue,

        -- Lifecycle
        min(o.order_date)                                   as first_order_date,
        max(o.order_date)                                   as last_order_date,
        date_diff(max(o.order_date), min(o.order_date), day) as customer_tenure_days,

        -- Delivery experience
        round(avg(o.actual_delivery_minutes), 1)            as avg_delivery_minutes,
        countif(o.is_on_time)                               as on_time_deliveries,
        round(safe_divide(countif(o.is_on_time),
              count(distinct o.order_id)) * 100, 2)         as on_time_pct,

        -- Basket
        round(avg(o.item_count), 1)                         as avg_basket_size,

        -- Issues
        countif(i.issue_count > 0)                          as orders_with_issues,
        round(safe_divide(
            countif(i.issue_count > 0),
            count(distinct o.order_id)
        ) * 100, 2)                                         as issue_rate_pct,

        -- Payment preference
        approx_top_count(o.payment_method, 1)[offset(0)].value
                                                            as preferred_payment_method,
        -- Platform preference
        approx_top_count(o.platform, 1)[offset(0)].value
                                                            as preferred_platform,

        -- Discount behaviour
        round(safe_divide(sum(o.discount), sum(o.revenue)) * 100, 2)
                                                            as avg_discount_pct

    from delivered_orders o
    left join issues i on o.order_id = i.order_id
    group by o.customer_id
),

-- ── Cancellation rate (across all statuses) ─────────────────────────────────
cancellation_stats as (
    select
        customer_id,
        count(distinct order_id)                            as total_orders_all,
        countif(order_status = 'CANCELLED')                 as cancelled_orders,
        round(safe_divide(
            countif(order_status = 'CANCELLED'),
            count(distinct order_id)
        ) * 100, 2)                                         as cancellation_rate_pct
    from all_orders
    group by customer_id
),

-- ── RFM scoring ─────────────────────────────────────────────────────────────
rfm_scored as (
    select
        *,
        -- RFM quintile scores (5 = best)
        -- Recency: lower days_since_last_order = better → order ASC
        ntile(5) over (order by days_since_last_order asc)  as recency_score,
        ntile(5) over (order by total_orders desc)          as frequency_score,
        ntile(5) over (order by lifetime_revenue desc)      as monetary_score
    from customer_stats
),

rfm_segmented as (
    select
        *,
        -- Composite score for quick sorting (555 = best, 111 = worst)
        (recency_score * 100) + (frequency_score * 10) + monetary_score
                                                            as rfm_score,
        case
            when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4
                then 'Champions'
            when recency_score >= 3 and frequency_score >= 4 and monetary_score >= 3
                then 'Loyal Customers'
            when recency_score >= 4 and frequency_score = 3
                then 'Potential Loyalists'
            when recency_score >= 4 and frequency_score <= 2
                then 'New Customers'
            when recency_score = 3  and frequency_score <= 3
                then 'Need Attention'
            when recency_score <= 2 and frequency_score >= 3
                then 'At Risk'
            when recency_score <= 2 and frequency_score <= 2 and monetary_score >= 3
                then 'Hibernating'
            when recency_score <= 2 and frequency_score <= 2 and monetary_score <= 2
                then 'Lost Customers'
            else 'Others'
        end                                                 as rfm_segment
    from rfm_scored
)

-- ── Final output ────────────────────────────────────────────────────────────
select
    -- Customer identity
    s.customer_id,
    c.city_name                         as customer_city,
    c.state_name                        as customer_state,
    c.is_pass_member,
    c.signup_date,
    c.days_since_signup,

    -- Order stats
    s.days_since_last_order,
    s.total_orders,
    s.first_order_date,
    s.last_order_date,
    s.customer_tenure_days,

    -- Financial
    s.lifetime_revenue,
    s.lifetime_net_revenue,
    s.avg_order_value,
    s.avg_discount_pct,

    -- Basket
    s.avg_basket_size,

    -- Delivery experience
    s.avg_delivery_minutes,
    s.on_time_deliveries,
    s.on_time_pct,

    -- Quality
    s.orders_with_issues,
    s.issue_rate_pct,

    -- Cancellations
    cs.cancelled_orders,
    cs.cancellation_rate_pct,

    -- Preferences
    s.preferred_payment_method,
    s.preferred_platform,

    -- RFM
    s.recency_score,
    s.frequency_score,
    s.monetary_score,
    s.rfm_score,
    s.rfm_segment

from rfm_segmented s
inner join customers c    on s.customer_id = c.customer_id
left  join cancellation_stats cs on s.customer_id = cs.customer_id