with source as (
    select * from `genai-copilot-enterprisedata`.`raw`.`events`
),

cleaned as (
    select
        cast(event_id       as string)      as event_id,
        concat(cast(customer_id as string), '_', cast(cast(event_timestamp as timestamp) as date)) as session_id,
        cast(customer_id    as string)      as customer_id,  -- nullable (anonymous users)

        lower(trim(event_type))             as event_type,   -- page_view, add_to_cart, purchase
        case when lower(trim(event_type)) = 'page_view' then '/product/details' else null end as page,
        case
            when customer_id is null or trim(cast(customer_id as string)) = '' then 'unknown'
            else case mod(abs(farm_fingerprint(cast(customer_id as string))), 3)
                when 0 then 'desktop' when 1 then 'mobile' else 'tablet'
            end
        end as device_type,

        cast(event_timestamp as timestamp)  as event_timestamp,
        cast(cast(event_timestamp as timestamp) as date) as event_date,

        current_timestamp()                 as _dbt_loaded_at

    from source
    where event_id is not null and event_timestamp is not null
)

select * from cleaned