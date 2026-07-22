

  create or replace view `genai-copilot-enterprisedata`.`staging`.`stg_events`
  OPTIONS()
  as with source as (
    select * from `genai-copilot-enterprisedata`.`raw`.`events`
),

cleaned as (
        select
            cast(event_id as string)              as event_id,
            cast(customer_id as string)           as customer_id,
            lower(trim(event_type))               as event_type,
            cast(event_timestamp as timestamp)    as event_timestamp,
            cast(cast(event_timestamp as timestamp) as date) as event_date,
            current_timestamp()                   as _dbt_loaded_at

        from source
        where event_id is not null
        and event_timestamp is not null  
)

select * from cleaned;

