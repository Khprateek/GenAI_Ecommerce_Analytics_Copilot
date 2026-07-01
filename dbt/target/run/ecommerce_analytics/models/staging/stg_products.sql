

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
        trim(brand)                     as brand,
        cast(null as string)            as sub_category,
        true                            as is_active,
        cast(cost_price as numeric)     as cost_price_usd,
        cast(price   as numeric)        as retail_price_usd,
        round(safe_divide(cast(price as numeric)-cast(cost_price as numeric),cast(price as numeric))*100,2) as margin_pct,
        
        current_timestamp()             as _dbt_loaded_at

    from source
    where product_id is not null
)

select * from cleaned;

