
  
    

    create or replace table `genai-copilot-enterprisedata`.`marts`.`dim_customers`
      
    
    

    
    OPTIONS()
    as (
      with customers as (
    select * from `genai-copilot-enterprisedata`.`staging`.`stg_customers`
),

customer_stats as (
    select * from `genai-copilot-enterprisedata`.`staging`.`int_customer_orders`
),

final as (
    select
        -- surrogate key (BigQuery-safe)
        to_hex(md5(cast(coalesce(cast(c.customer_id as string), '_dbt_utils_surrogate_key_null_') as string))) as customer_sk,

        -- natural key
        c.customer_id,

        -- personal attributes
        c.first_name,
        c.last_name,
        concat(c.first_name, ' ', c.last_name)  as full_name,
        c.email,
        c.country_code,
        c.city,

        -- signup info
        c.signup_date,
        c.acquisition_channel,
        c.days_since_signup,

        -- RFM metrics (from intermediate)
        coalesce(cs.total_orders, 0)              as total_orders,
        coalesce(cs.lifetime_value_usd, 0)        as lifetime_value_usd,
        coalesce(cs.avg_order_value_usd, 0)       as avg_order_value_usd,
        cs.days_since_last_order,
        cs.first_order_date,
        cs.last_order_date,
        cs.preferred_channel,

        -- RFM scores
        cs.recency_score,
        cs.frequency_score,
        cs.monetary_score,
        coalesce(cs.rfm_segment, 'No Purchases')  as rfm_segment,

        -- value tier
        case
            when coalesce(cs.lifetime_value_usd, 0) >= 1000 then 'High Value'
            when coalesce(cs.lifetime_value_usd, 0) >= 300  then 'Mid Value'
            when coalesce(cs.lifetime_value_usd, 0) > 0     then 'Low Value'
            else 'No Purchase'
        end                                        as value_tier

    from customers c
    left join customer_stats cs on c.customer_id = cs.customer_id
)

select * from final
    );
  