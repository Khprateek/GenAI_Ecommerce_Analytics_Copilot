with source as (
    select * from {{ source('raw', 'marketing_spend') }}
),

cleaned as (
    select
        cast(spend_id as string) as spend_id,
        cast(date as date) as spend_date,
        lower(trim(channel)) as channel,
        cast(spend_inr as numeric) as spend_inr,
        cast(impressions as integer) as impressions,
        cast(clicks as integer) as clicks,
        cast(app_installs as integer) as app_installs,
        round(safe_divide(cast(spend_inr as numeric),cast(clicks as numeric)),4) as cpc_inr,
        round(safe_divide(cast(clicks as numeric),cast(impressions as numeric))*100,4) as ctr_pct,
        current_timestamp() as _dbt_loaded_at
    from source where spend_id is not null)
select * from cleaned