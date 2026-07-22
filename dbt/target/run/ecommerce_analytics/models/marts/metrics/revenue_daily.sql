
  
    

    create or replace table `genai-copilot-enterprisedata`.`metrics`.`revenue_daily`
      
    
    

    
    OPTIONS()
    as (
      -- Pre-aggregated daily revenue — Streamlit queries this directly
-- Much cheaper than querying fact_orders every time

with fact as (
    select * from `genai-copilot-enterprisedata`.`marts`.`fact_orders`
),

daily as (
    select
        order_date,
        order_year,
        order_month,
        order_week,

        -- breakdowns
        state_name,
        city_name,
        customer_type,

        -- channel (join back to get name)
        dch.channel_name,
        dch.channel_type,

        -- measures
        count(distinct order_id)                                                    as total_orders,
        count(distinct customer_sk)                                                 as unique_customers,
        sum(case when is_completed = 1 then revenue_usd else 0 end)                 as gross_revenue_usd,
        sum(case when is_completed = 1 then discount_usd else 0 end)                as total_discounts_usd,
        sum(case when is_completed = 1 then net_revenue_usd else 0 end)             as net_revenue_usd,
        sum(total_items)                                                            as total_items_sold,
        sum(is_cancelled)                                                           as cancelled_orders,
        SAFE_DIVIDE(COUNT(DISTINCT order_id) - SUM(is_cancelled),COUNT(DISTINCT order_id)) AS order_fullfillment_rate,
        SAFE_DIVIDE(SUM(total_items), COUNT(DISTINCT order_id)) AS basket_depth,
        SAFE_DIVIDE(SUM(CASE WHEN is_completed = 1 THEN revenue_usd ELSE 0 END), COUNT(CASE WHEN is_completed = 1 THEN 1 END)) AS avg_order_value


    from fact
    left join `genai-copilot-enterprisedata`.`marts`.`dim_channels` dch on fact.channel_sk = dch.channel_sk
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9
)

select * from daily
    );
  