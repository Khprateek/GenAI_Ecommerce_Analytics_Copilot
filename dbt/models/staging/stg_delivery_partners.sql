with source as (
    select *
    from {{ source('raw', 'delivery_partners') }}
),

cleaned as (

    select
        cast(rider_id as string)                    as rider_id,

        trim(name)                                  as full_name,
        trim(split(name, ' ')[safe_offset(0)])      as first_name,
        trim(split(name, ' ')[safe_offset(1)])      as last_name,

        upper(trim(store_id))                       as home_store_id,
        upper(trim(city))                           as city_name,

        initcap(trim(vehicle_type))                 as vehicle_type,

        cast(join_date as date)                     as join_date,

        date_diff(current_date(), cast(join_date as date), day)
                                                    as days_since_join,
        current_timestamp()                         as _dbt_loaded_at

    from source

    where rider_id is not null

)

select *
from cleaned