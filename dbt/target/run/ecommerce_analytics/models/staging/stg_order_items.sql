

  create or replace view `genai-copilot-enterprisedata`.`staging`.`stg_order_items`
  OPTIONS()
  as with source as (
    select * from `genai-copilot-enterprisedata`.`raw`.`order_items`
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

select * from cleaned;

