with products as (
    select * from `genai-copilot-enterprisedata`.`staging`.`stg_products`
),

product_perf as (
    select * from `genai-copilot-enterprisedata`.`staging`.`int_product_revenue`
),

final as (
    select
        to_hex(md5(cast(coalesce(cast(p.product_id as string), '_dbt_utils_surrogate_key_null_') as string))) as product_sk,

        p.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        p.brand,
        p.is_active,

        -- pricing
        p.cost_price_usd,
        p.retail_price_usd,
        p.margin_pct,

        -- price tier
        case
            when p.retail_price_usd >= 200 then 'Premium'
            when p.retail_price_usd >= 50  then 'Mid-Range'
            else 'Budget'
        end as price_tier,

        -- performance (from intermediate)
        coalesce(pp.total_orders, 0)        as total_orders,
        coalesce(pp.total_units_sold, 0)    as total_units_sold,
        coalesce(pp.total_revenue_usd, 0)   as total_revenue_usd,
        coalesce(pp.gross_profit_usd, 0)    as gross_profit_usd,

        -- performance label
        case
            when coalesce(pp.total_revenue_usd, 0) >= 50000 then 'Top Seller'
            when coalesce(pp.total_revenue_usd, 0) >= 10000 then 'Good Seller'
            when coalesce(pp.total_revenue_usd, 0) > 0      then 'Slow Mover'
            else 'No Sales'
        end as sales_performance

    from products p
    left join product_perf pp on p.product_id = pp.product_id
)

select * from final