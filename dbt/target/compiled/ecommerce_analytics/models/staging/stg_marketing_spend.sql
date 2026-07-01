with source as (
    select * from `genai-copilot-enterprisedata`.`raw`.`marketing_spend`
),

cleaned as (
    select
        cast(spend_id as string) as spend_id,
        cast(date as date) as spend_date,
        lower(trim(channel)) as channel,
        cast(spend_usd as numeric) as spend_usd,
        cast(impressions as integer) as impressions,
        cast(clicks as integer) as clicks,
        round(safe_divide(cast(spend_usd as numeric),cast(clicks as numeric)),4) as cpc_usd,
        round(safe_divide(cast(clicks as numeric),cast(impressions as numeric))*100,4) as ctr_pct,
        current_timestamp() as _dbt_loaded_at
    from source where spend_id is not null)
select * from cleaned