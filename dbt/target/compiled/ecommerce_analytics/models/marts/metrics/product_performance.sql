select
    product_id,
    product_name,
    category,
    sub_category,
    brand,
    price_tier,
    sales_performance,
    retail_price_usd,
    cost_price_usd,
    margin_pct,
    total_orders,
    total_units_sold,
    total_revenue_usd,
    gross_profit_usd,
    is_active
from `genai-copilot-enterprisedata`.`marts`.`dim_products`
order by total_revenue_usd desc