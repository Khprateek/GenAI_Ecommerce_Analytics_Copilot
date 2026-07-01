

  create or replace view `genai-copilot-enterprisedata`.`staging`.`stg_products`
  OPTIONS()
  as with source as (
    select * from `genai-copilot-enterprisedata`.`raw`.`products`
),

cleaned as (
    select
        cast(product_id     as string)  as product_id,
        trim(product_name)              as product_name,
        trim(category)                  as category,
        cast(null as string)            as sub_category,
        cast(null as string)            as brand,
        true                            as is_active,
        cast(price * 0.70 as numeric)   as cost_price_usd,
        cast(price   as numeric)        as retail_price_usd,
        cast(30.0 as numeric)           as margin_pct,
        
        current_timestamp()             as _dbt_loaded_at

    from source
    where product_id is not null
)

select * from cleaned;

