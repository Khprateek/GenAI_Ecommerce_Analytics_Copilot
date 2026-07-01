select
    customer_id,
    full_name,
    email,
    country_code,
    acquisition_channel,
    signup_date,
    rfm_segment,
    value_tier,
    total_orders,
    lifetime_value_usd,
    avg_order_value_usd,
    days_since_last_order,
    first_order_date,
    last_order_date,
    preferred_channel,
    recency_score,
    frequency_score,
    monetary_score
from {{ ref('dim_customers') }}
where total_orders > 0