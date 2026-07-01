-- fact_orders: one row per order
-- All foreign keys (SKs) point to dimension tables
-- All measures are additive

with orders as (
    select * from {{ ref('int_orders_enriched') }}
),

dim_customers as (
    select customer_sk, customer_id from {{ ref('dim_customers') }}
),

dim_products as (
    -- We need product_sk per order — use most expensive item as primary product
    select
        oi.order_id,
        dp.product_sk
    from {{ ref('stg_order_items') }} oi
    inner join {{ ref('dim_products') }} dp on oi.product_id = dp.product_id
    qualify row_number() over (
        partition by oi.order_id
        order by oi.line_revenue_usd desc
    ) = 1
),

dim_channels as (
    select channel_sk, channel_code from {{ ref('dim_channels') }}
),

dim_date as (
    select date_key, full_date from {{ ref('dim_date') }}
),

final as (
    select
        -- surrogate key for the fact row
        {{ dbt_utils.generate_surrogate_key(['o.order_id']) }} as order_sk,

        -- natural key (keep for debugging)
        o.order_id,

        -- foreign keys → dimensions
        dc.customer_sk,
        dp.product_sk,
        dch.channel_sk,
        dd.date_key                                     as order_date_key,

        -- degenerate dimensions (attributes that don't need their own dim)
        o.order_status,
        o.country_code,
        o.customer_type,                                -- new vs returning

        -- DATE (also store raw date for easy filtering)
        o.order_date,
        o.order_year,
        o.order_month,
        o.order_week,

        -- MEASURES (all additive)
        o.revenue_usd,
        o.discount_usd,
        o.shipping_cost_usd,
        o.net_revenue_usd,
        o.total_items,
        o.unique_products,

        -- derived measures
        o.revenue_usd - o.discount_usd                 as discounted_revenue_usd,
        case when o.order_status = 'COMPLETED' then 1 else 0 end as is_completed,
        case when o.order_status = 'CANCELLED' then 1 else 0 end as is_cancelled

    from orders o
    left join dim_customers  dc  on o.customer_id   = dc.customer_id
    left join dim_products   dp  on o.order_id      = dp.order_id
    left join dim_channels   dch on o.channel       = dch.channel_code
    left join dim_date       dd  on o.order_date    = dd.full_date
)

select * from final
