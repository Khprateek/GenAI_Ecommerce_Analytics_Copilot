

  create or replace view `genai-copilot-enterprisedata`.`staging`.`stg_products`
  OPTIONS()
  as with source as (
    select * from `genai-copilot-enterprisedata`.`raw`.`products`
),

cleaned as (
    select

        -- Primary Key
        cast(product_id as string)                     as product_id,

        -- Product Details
        trim(product_name)                             as product_name,
        trim(category)                                 as category_name,
        trim(brand)                                    as brand_name,
        lower(trim(pack_size))                         as pack_size,

        -- Pricing
        cast(mrp as numeric)                           as mrp,
        cast(selling_price as numeric)                 as selling_price,
        cast(cost_price as numeric)                    as cost_price,

        -- Attributes
        cast(is_perishable as bool)                    as is_perishable,
        cast(shelf_life_days as int64)                 as shelf_life_days,

        -- Audit
        current_timestamp()                            as _dbt_loaded_at

    from source
    where
        product_id is not null
        and product_name is not null

)

select * from cleaned;

