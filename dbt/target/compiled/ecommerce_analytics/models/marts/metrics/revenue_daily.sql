-- Pre-aggregated daily revenue — Streamlit queries this directly
-- Much cheaper than querying fact_orders every time

with fact as (
    select * from `genai-copilot-enterprisedata`.`marts`.`fact_orders`
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

    from fact
    left join `genai-copilot-enterprisedata`.`marts`.`dim_channels` dch on fact.channel_sk = dch.channel_sk
    group by 1, 2, 3, 4, 5, 6, 7, 8
)

select * from daily