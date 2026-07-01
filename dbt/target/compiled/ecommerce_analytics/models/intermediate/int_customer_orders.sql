-- Per-customer aggregated purchase history
-- Used to compute RFM segments in dim_customers

with orders as (
    select * from `genai-copilot-enterprisedata`.`staging`.`stg_orders`
    where order_status = 'COMPLETED'
),

customer_stats as (
    select
        customer_id,

        -- Recency: days since last order
        date_diff(current_date(), max(order_date), day)   as days_since_last_order,

        -- Frequency
        count(distinct order_id)                           as total_orders,

        -- Monetary
        sum(revenue_usd)                                   as lifetime_value_usd,
        avg(revenue_usd)                                   as avg_order_value_usd,

        -- First & last order
        min(order_date)                                    as first_order_date,
        max(order_date)                                    as last_order_date,

        -- Preferred channel
        approx_top_count(channel, 1)[offset(0)].value     as preferred_channel

    from orders
    group by customer_id
),

rfm_scored as (
    select
        *,
        -- RFM quintile scoring (1=worst, 5=best)
        ntile(5) over (order by days_since_last_order desc) as recency_score,
        ntile(5) over (order by total_orders asc)           as frequency_score,
        ntile(5) over (order by lifetime_value_usd asc)     as monetary_score
    from customer_stats
),

segmented as (
    select
        *,
        -- Simple segment based on combined RFM
        case
            when recency_score >= 4 and frequency_score >= 4 then 'Champions'
            when recency_score >= 3 and frequency_score >= 3 then 'Loyal Customers'
            when recency_score >= 4 and frequency_score <= 2 then 'New Customers'
            when recency_score <= 2 and frequency_score >= 3 then 'At Risk'
            when recency_score <= 2 and frequency_score <= 2 then 'Lost'
            else 'Potential Loyalists'
        end as rfm_segment
    from rfm_scored
)

select * from segmented