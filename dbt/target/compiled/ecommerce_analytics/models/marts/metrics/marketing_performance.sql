with spend as (select * from `genai-copilot-enterprisedata`.`staging`.`stg_marketing_spend`),
rev as (
    select order_date, channel, sum(revenue_usd) as revenue_usd, count(distinct order_id) as orders
    from `genai-copilot-enterprisedata`.`staging`.`stg_orders` where order_status = "COMPLETED" group by 1,2)
select
    s.spend_date, s.channel, s.spend_usd, s.impressions, s.clicks, s.cpc_usd, s.ctr_pct,
    coalesce(r.revenue_usd,0) as attributed_revenue_usd,
    coalesce(r.orders,0) as attributed_orders,
    round(safe_divide(coalesce(r.revenue_usd,0), s.spend_usd),2) as roas,
    round(safe_divide(s.spend_usd, coalesce(r.orders,0)),2) as cac_usd
from spend s
left join rev r on s.spend_date = r.order_date and s.channel = r.channel
order by spend_date desc