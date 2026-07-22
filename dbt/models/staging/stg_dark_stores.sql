with source as (
    select * from {{ source('raw', 'dark_stores') }}
),

cleaned as (
    select
        cast(store_id   as string)                  as store_id,
        upper(trim(city))                           as city_name,
        upper(trim(state))                          as state_name,
        upper(trim(locality))                       as locality,
        cast(latitude as numeric)                   as latitude,
        cast(longitude as numeric)                  as longitude,

        cast(sku_capacity as int64)                 as sku_capacity,
        cast(delivery_radius_km as numeric)         as delivery_radius_km,

        cast(launch_date as date)                   as launch_date,

        -- derived: days since signup
        date_diff(current_date(), cast(launch_date as date), day) as days_since_launch,
        current_timestamp()                         as _dbt_loaded_at

    from source
    where store_id is not null
)

select * from cleaned