-- stg_orders: clean column names, cast types, filter bad rows
-- Raw → Staging: rename, cast, no business logic yet

with source as (
    select * from {{ source('raw', 'orders') }}
),

cleaned as (
    select
        -- Primary key
        cast(order_id as string)                            as order_id,

        --Business Keys
        cast(customer_id as string)                         as customer_id,
        cast(store_id as string)                            as store_id,
        cast(rider_id as string)                            as rider_id,

        -- Order Timestamp
        cast(order_datetime as timestamp)                   as order_timestamp,
        cast(order_datetime as date)                        as order_date,

        -- Status
        upper(trim(status))                                 as order_status,

        -- attributes
        upper(trim(payment_method))                         as payment_method,
        initcap(trim(platform))                             as platform,

        -- Delivery
        SAFE_CAST(promised_delivery_minutes as int64)            as promised_delivery_minutes,
        SAFE_CAST(actual_delivery_minutes as int64)              as actual_delivery_minutes,
        SAFE_CAST(is_on_time as bool)                            as is_on_time,

        -- Basket
        cast(item_count as int64)                           as item_count,

        -- Monetary
        cast(revenue as numeric)                            as revenue,
        cast(discount as numeric)                           as discount,
        cast(delivery_fee as numeric)                       as delivery_fee,

        -- Audit
        current_timestamp()               as _dbt_loaded_at

    from source

    where
        order_id     is not null
        and customer_id is not null
        and order_datetime  is not null
)

select * from cleaned