-- Pre-aggregated daily revenue — Streamlit queries this directly
-- Much cheaper than querying fact_orders every time

with fact as (
    select * from {{ ref('fact_orders') }}
    where is_completed = 1
),

daily as (
    select
        order_date,
        order_year,
        order_month,
        order_week,

        -- breakdowns
        country_code,
        customer_type,

        -- channel (join back to get name)
        dch.channel_name,
        dch.channel_type,

        -- measures
        count(distinct order_id)        as total_orders,
        count(distinct customer_sk)     as unique_customers,
        sum(revenue_usd)                as gross_revenue_usd,
        sum(discount_usd)               as total_discounts_usd,
        sum(net_revenue_usd)            as net_revenue_usd,
        sum(total_items)                as total_items_sold,
        avg(revenue_usd)                as avg_order_value_usd,
        sum(is_cancelled)               as cancelled_orders
        coalesce(rd.refunds_usd,0)      as refunds_usd,
        coalesce(rd.return_count,0)     as return_count,
        sum(f.revenue_usd) - coalesce(rd.refunds_usd,0) as revenue_after_returns_usd

    from fact
    left join {{ ref('dim_channels') }} dch on fact.channel_sk = dch.channel_sk
    left join rd on f.order_date = rd.return_date
    group by 1,2,3,4,5,6,7,16,17
)

select * from daily
