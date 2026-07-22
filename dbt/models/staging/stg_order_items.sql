with source as (
    select * from {{ source('raw', 'order_items') }}
),

cleaned as (
    select
        cast(order_item_id  as string)              as item_id,
        cast(order_id       as string)              as order_id,
        cast(product_id     as string)              as product_id,

        cast(quantity       as integer)             as quantity,
        cast(unit_price     as numeric)             as unit_price,
        cast(is_substituted as bool)                as is_substituted,


        -- derived: actual line revenue
        round(
            cast(quantity as numeric) * cast(unit_price as numeric)
            * (1 - coalesce(cast(0 as numeric), 0) / 100),
            2
        )                               as line_revenue,
        current_timestamp()             as _dbt_loaded_at

    from source
    where order_item_id is not null and order_id is not null
)

select * from cleaned