-- ============================================================================
-- int_customer_churn_features.sql
-- ============================================================================
-- Builds a feature vector per customer for churn prediction / early-warning.
-- Compares recent behaviour (last 30 days) against lifetime averages to
-- detect drop-offs in frequency, basket value, and delivery satisfaction.
--
-- Grain: one row per customer_id
-- Depends on: stg_customers, stg_orders, stg_order_issues, stg_events
-- ============================================================================

with customers as (
    select
        customer_id,
        is_pass_member,
        signup_date,
        days_since_signup
    from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
    where order_status = 'DELIVERED'
),

issues as (
    select order_id, count(issue_id) as issue_count
    from {{ ref('stg_order_issues') }}
    group by order_id
),

events as (
    select customer_id, event_date, event_type
    from {{ ref('stg_events') }}
    where customer_id is not null
),

-- ── Lifetime order metrics ──────────────────────────────────────────────────
lifetime_metrics as (
    select
        o.customer_id,

        date_diff(current_date(), max(o.order_date), day)
                                                    as days_since_last_order,
        count(distinct o.order_id)                  as lifetime_orders,
        round(avg(o.revenue), 2)                    as avg_order_value_lifetime,
        round(avg(o.actual_delivery_minutes), 1)    as avg_delivery_min_lifetime,
        round(safe_divide(countif(o.is_on_time),
              count(distinct o.order_id)) * 100, 2) as on_time_pct_lifetime,
        round(safe_divide(countif(i.issue_count > 0),
              count(distinct o.order_id)) * 100, 2) as issue_rate_pct_lifetime

    from orders o
    left join issues i on o.order_id = i.order_id
    group by o.customer_id
),

-- ── Last-30-day order metrics ───────────────────────────────────────────────
recent_metrics as (
    select
        o.customer_id,

        count(distinct o.order_id)                  as orders_30d,
        round(avg(o.revenue), 2)                    as avg_order_value_30d,
        round(avg(o.actual_delivery_minutes), 1)    as avg_delivery_min_30d,
        round(safe_divide(countif(o.is_on_time),
              nullif(count(distinct o.order_id), 0)) * 100, 2)
                                                    as on_time_pct_30d,
        round(safe_divide(countif(i.issue_count > 0),
              nullif(count(distinct o.order_id), 0)) * 100, 2)
                                                    as issue_rate_pct_30d

    from orders o
    left join issues i on o.order_id = i.order_id
    where o.order_date >= date_sub(current_date(), interval 30 day)
    group by o.customer_id
),

-- ── Event engagement in last 30 days ────────────────────────────────────────
recent_engagement as (
    select
        customer_id,
        count(*)                                    as events_30d,
        countif(event_type = 'page_view')           as page_views_30d,
        countif(event_type = 'add_to_cart')          as add_to_carts_30d,
        countif(event_type = 'purchase')             as purchases_30d,
        count(distinct event_date)                  as active_days_30d
    from events
    where event_date >= date_sub(current_date(), interval 30 day)
    group by customer_id
),

-- ── Assemble feature vector ─────────────────────────────────────────────────
features as (
    select
        c.customer_id,
        c.is_pass_member,
        c.days_since_signup,

        -- Recency
        coalesce(lm.days_since_last_order, 999)     as days_since_last_order,

        -- Frequency trend
        coalesce(lm.lifetime_orders, 0)             as lifetime_orders,
        coalesce(rm.orders_30d, 0)                  as orders_30d,

        -- AOV trend (negative = declining spend)
        round(
            coalesce(rm.avg_order_value_30d, 0)
            - coalesce(lm.avg_order_value_lifetime, 0),
            2
        )                                           as aov_trend,

        -- Delivery experience trend
        round(
            coalesce(rm.avg_delivery_min_30d, 0)
            - coalesce(lm.avg_delivery_min_lifetime, 0),
            1
        )                                           as delivery_time_trend,

        coalesce(lm.on_time_pct_lifetime, 0)        as on_time_pct_lifetime,
        coalesce(rm.on_time_pct_30d, 0)             as on_time_pct_30d,

        -- Issue rate trend (positive = worsening quality)
        round(
            coalesce(rm.issue_rate_pct_30d, 0)
            - coalesce(lm.issue_rate_pct_lifetime, 0),
            2
        )                                           as issue_rate_trend,

        -- App engagement (last 30 days)
        coalesce(re.events_30d, 0)                  as events_30d,
        coalesce(re.active_days_30d, 0)             as active_days_30d,
        coalesce(re.page_views_30d, 0)              as page_views_30d,
        coalesce(re.add_to_carts_30d, 0)            as add_to_carts_30d,

        -- ── Churn risk label ────────────────────────────────────────────────
        case
            when coalesce(lm.days_since_last_order, 999) > 90
                then 'Churned'
            when coalesce(lm.days_since_last_order, 999) > 45
                 or (coalesce(rm.orders_30d, 0) = 0 and coalesce(lm.lifetime_orders, 0) >= 3)
                then 'High Risk'
            when coalesce(lm.days_since_last_order, 999) > 21
                 or coalesce(rm.avg_order_value_30d, 0) < coalesce(lm.avg_order_value_lifetime, 0) * 0.5
                then 'Medium Risk'
            when coalesce(rm.orders_30d, 0) > 0
                then 'Active'
            else 'Dormant'
        end                                         as churn_risk_tier

    from customers c
    left join lifetime_metrics lm on c.customer_id = lm.customer_id
    left join recent_metrics   rm on c.customer_id = rm.customer_id
    left join recent_engagement re on c.customer_id = re.customer_id
)

select * from features
