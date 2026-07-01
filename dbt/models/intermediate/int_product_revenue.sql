with items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select order_id, order_date, order_status
    from {{ ref('stg_orders') }}
    where order_status = 'COMPLETED'
),

products as (
    select * from {{ ref('stg_products') }}
),

product_revenue as (
    select
        i.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        p.brand,
        p.cost_price_usd,
        p.retail_price_usd,
        p.margin_pct,

        count(distinct i.order_id)          as total_orders,
        sum(i.quantity)                     as total_units_sold,
        sum(i.line_revenue_usd)             as total_revenue_usd,
        avg(i.unit_price_usd)               as avg_selling_price_usd,

        -- profitability
        sum(i.line_revenue_usd)
            - sum(i.quantity * p.cost_price_usd) as gross_profit_usd

    from items i
    inner join orders o on i.order_id = o.order_id
    left join products p on i.product_id = p.product_id
    group by 1,2,3,4,5,6,7,8
)

select * from product_revenue
