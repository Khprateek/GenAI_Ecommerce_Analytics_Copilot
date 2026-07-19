

  create or replace view `genai-copilot-enterprisedata`.`staging`.`int_orders_enriched`
  OPTIONS()
  as -- Joins orders with their items and customer info
-- This becomes the base for fact_orders

with orders as (
    select * from `genai-copilot-enterprisedata`.`staging`.`stg_orders`
),

order_items_agg as (
    select
        order_id,
        sum(quantity)           as total_items,
        sum(line_revenue_usd)   as items_revenue_usd,
        count(distinct product_id) as unique_products
    from `genai-copilot-enterprisedata`.`staging`.`stg_order_items`
    group by order_id
),

customers as (
    select
        customer_id,
        state_name            as customer_state,
        city_name             as customer_city,
        acquisition_channel,
        signup_date,
        days_since_signup
    from `genai-copilot-enterprisedata`.`staging`.`stg_customers`
),

returns_agg as (
    select
        order_id,
        sum(refund_amount_usd) as total_refund_usd
    from `genai-copilot-enterprisedata`.`staging`.`stg_returns`
    group by order_id
),

enriched as (
    select
        -- order keys
        o.order_id,
        o.customer_id,

        -- dates
        o.order_date,
        extract(year  from o.order_date) as order_year,
        extract(month from o.order_date) as order_month,
        extract(week  from o.order_date) as order_week,

        -- order attributes
        o.order_status,
        o.channel,
        c.customer_state              as state_name,
        c.customer_city               as city_name,

        -- financials
        o.revenue_usd,
        o.discount_usd,
        o.shipping_cost_usd,
        coalesce(r.total_refund_usd, 0) as refund_usd,
        o.revenue_usd - coalesce(o.discount_usd, 0) - coalesce(r.total_refund_usd, 0) as net_revenue_usd,

        -- items
        coalesce(oi.total_items, 0)       as total_items,
        coalesce(oi.unique_products, 0)   as unique_products,

        -- customer context
        c.days_since_signup,
        -- new vs returning: first order?
        case
            when c.signup_date = o.order_date then 'new'
            else 'returning'
        end                               as customer_type

    from orders o
    left join order_items_agg oi on o.order_id = oi.order_id
    left join customers c on o.customer_id = c.customer_id
    left join returns_agg r on o.order_id = r.order_id
)

select * from enriched;

