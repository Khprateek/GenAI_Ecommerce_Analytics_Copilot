-- stg_orders: clean column names, cast types, filter bad rows
-- Raw → Staging: rename, cast, no business logic yet

with source as (
    select * from {{ source('raw', 'orders') }}
),

cleaned as (
    select
        -- keys
        cast(order_id       as string)    as order_id,
        cast(customer_id    as string)    as customer_id,

        -- dates
        cast(order_date     as date)      as order_date,
        cast(cast(order_date as date) as timestamp) as updated_at,

        -- attributes
        case upper(trim(status)) when 'RETURNED' then 'REFUNDED' else upper(trim(status)) end as order_status,   -- COMPLETED, CANCELLED etc.
        lower(trim(channel))              as channel,        -- web, mobile, store

        -- amounts (ensure non-negative)
        cast(revenue        as numeric)   as revenue_usd,
        cast(discount       as numeric)   as discount_usd,
        cast(10.00          as numeric)   as shipping_cost_usd,

        -- metadata
        current_timestamp()               as _dbt_loaded_at

    from source

    where
        order_id     is not null
        and customer_id is not null
        and order_date  is not null
        and revenue     >= 0              -- drop corrupted negative revenue rows
)

select * from cleaned