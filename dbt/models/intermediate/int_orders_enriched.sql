-- ============================================================================
-- int_orders_enriched.sql
-- ============================================================================
-- Enriches every order with item aggregates, customer profile, dark-store
-- location, rider info, and order-issue summaries.
-- This is the single "wide order fact" that all downstream marts consume.
--
-- Grain: one row per order_id
-- Depends on: stg_orders, stg_order_items, stg_customers, stg_dark_stores,
--             stg_delivery_partners, stg_order_issues
-- ============================================================================

with orders as (
    select * from {{ ref('stg_orders') }}
),

-- ── Line-item roll-up ───────────────────────────────────────────────────────
order_items_agg as (
    select
        order_id,
        sum(quantity)                           as total_items_quantity,
        sum(line_revenue)                       as items_revenue,
        count(distinct product_id)              as unique_products,
        countif(is_substituted)                 as substituted_item_count,
        logical_or(is_substituted)              as has_substitution
    from {{ ref('stg_order_items') }}
    group by order_id
),

-- ── Customer context ────────────────────────────────────────────────────────
customers as (
    select
        customer_id,
        first_name,
        last_name,
        state_name,
        city_name,
        home_locality,
        home_store_id,
        is_pass_member,
        signup_date,
        days_since_signup
    from {{ ref('stg_customers') }}
),

-- ── Dark-store geography ────────────────────────────────────────────────────
dark_stores as (
    select
        store_id,
        city_name       as store_city,
        state_name      as store_state,
        locality        as store_locality
    from {{ ref('stg_dark_stores') }}
),

-- ── Rider context ───────────────────────────────────────────────────────────
riders as (
    select
        rider_id,
        full_name       as rider_name,
        vehicle_type    as rider_vehicle_type
    from {{ ref('stg_delivery_partners') }}
),

-- ── Order-issue roll-up (replaces legacy returns) ───────────────────────────
issues_agg as (
    select
        order_id,
        count(issue_id)                         as issue_count,
        sum(refund_amount)                      as total_refund_amount,
        -- most common issue type per order
        approx_top_count(issue_type, 1)[offset(0)].value as primary_issue_type
    from {{ ref('stg_order_issues') }}
    group by order_id
),

-- ── Final enrichment ────────────────────────────────────────────────────────
enriched as (
    select

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Keys                                                           ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        o.order_id,
        o.customer_id,
        o.store_id,
        o.rider_id,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Timestamps & Calendar                                          ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        o.order_timestamp,
        o.order_date,
        extract(year  from o.order_date)            as order_year,
        extract(month from o.order_date)            as order_month,
        extract(week  from o.order_date)            as order_week,
        extract(dayofweek from o.order_date)        as order_day_of_week,
        extract(hour from o.order_timestamp)        as order_hour,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Order Attributes                                               ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        o.order_status,
        o.payment_method,
        o.platform,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Delivery Performance  (Quick-Commerce KPIs)                    ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        o.promised_delivery_minutes,
        o.actual_delivery_minutes,
        o.is_on_time,

        case
            when o.order_status != 'DELIVERED'      then null
            when o.actual_delivery_minutes is null   then null
            when o.actual_delivery_minutes > o.promised_delivery_minutes
                then o.actual_delivery_minutes - o.promised_delivery_minutes
            else 0
        end                                         as delivery_delay_minutes,

        case
            when o.order_status != 'DELIVERED'       then 'Not Delivered'
            when o.actual_delivery_minutes is null    then 'Unknown'
            when o.actual_delivery_minutes <= 10      then '0-10 min'
            when o.actual_delivery_minutes <= 15      then '11-15 min'
            when o.actual_delivery_minutes <= 20      then '16-20 min'
            else '20+ min'
        end                                         as delivery_time_bucket,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Location Context                                               ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        c.city_name                                 as customer_city,
        c.state_name                                as customer_state,
        c.home_locality                             as customer_home_locality,
        ds.store_city,
        ds.store_state,
        ds.store_locality,

        -- Did the customer order from their home store?
        (o.store_id = c.home_store_id)              as is_home_store_order,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Rider Context                                                  ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        r.rider_name,
        r.rider_vehicle_type,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Basket Metrics                                                 ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        coalesce(oi.total_items_quantity, o.item_count)  as total_items,
        coalesce(oi.unique_products, 0)                  as unique_products,
        coalesce(oi.substituted_item_count, 0)           as substituted_item_count,
        coalesce(oi.has_substitution, false)              as has_substitution,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Financials (INR)                                               ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        o.revenue,
        coalesce(o.discount, 0)                     as discount,
        coalesce(o.delivery_fee, 0)                 as delivery_fee,
        coalesce(i.total_refund_amount, 0)          as refund_amount,

        -- gross revenue = basket revenue + delivery fee
        round(o.revenue + coalesce(o.delivery_fee, 0), 2)
                                                    as gross_revenue,
        -- net revenue = gross - discount - refunds
        round(
            o.revenue
            + coalesce(o.delivery_fee, 0)
            - coalesce(o.discount, 0)
            - coalesce(i.total_refund_amount, 0),
            2
        )                                           as net_revenue,

        -- discount depth: what fraction of the basket was discounted?
        round(
            safe_divide(coalesce(o.discount, 0), nullif(o.revenue, 0)) * 100,
            2
        )                                           as discount_pct,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Order Issues                                                   ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        coalesce(i.issue_count, 0)                  as issue_count,
        coalesce(i.issue_count, 0) > 0              as has_order_issue,
        i.primary_issue_type,

        -- ╔═══════════════════════════════════════════════════════════════════╗
        -- ║  Customer Context & Segmentation Helpers                        ║
        -- ╚═══════════════════════════════════════════════════════════════════╝
        c.is_pass_member,
        c.signup_date                               as customer_signup_date,
        c.days_since_signup,

        case
            when c.signup_date = o.order_date then 'New'
            else 'Returning'
        end                                         as customer_type,

        case
            when o.revenue < 200  then 'Micro'
            when o.revenue < 500  then 'Small'
            when o.revenue < 1000 then 'Medium'
            else 'Large'
        end                                         as basket_size_tier

    from orders o
    left join order_items_agg  oi on o.order_id    = oi.order_id
    left join customers         c on o.customer_id = c.customer_id
    left join dark_stores      ds on o.store_id    = ds.store_id
    left join riders            r on o.rider_id    = r.rider_id
    left join issues_agg        i on o.order_id    = i.order_id
)

select * from enriched