with customers as (
    select customer_id from {{ ref('stg_customers') }}
),

order_metrics as (
    select
        customer_id,
        date_diff(current_date(), max(order_date), day) as days_since_last_order,
        count(distinct case when order_date >= date_add(current_date(), interval -30 day) then order_id end) as order_frequency_30d,
        avg(revenue_usd) as avg_order_value_lifetime,
        avg(case when order_date >= date_add(current_date(), interval -30 day) then revenue_usd end) as avg_order_value_30d
    from {{ ref('stg_orders') }}
    where order_status = 'COMPLETED'
    group by customer_id
),

final as (
    select
        c.customer_id,
        coalesce(om.days_since_last_order, 999) as days_since_last_order,
        coalesce(om.order_frequency_30d, 0) as order_frequency_30d,
        coalesce(om.avg_order_value_30d, 0) - coalesce(om.avg_order_value_lifetime, 0) as avg_order_value_trend
    from customers c
    left join order_metrics om on c.customer_id = om.customer_id
)

select * from final
