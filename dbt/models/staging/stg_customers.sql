with source as (
    select * from {{ source('raw', 'customers') }}
),

cleaned as (
    select
        cast(customer_id as string)             as customer_id,
        trim(split(name, ' ')[safe_offset(0)])  as first_name,
        trim(split(name, ' ')[safe_offset(1)])  as last_name,
        lower(concat(split(email, '@')[safe_offset(0)], '_', cast(customer_id as string), '@', split(email, '@')[safe_offset(1)])) as email,
        upper(trim(state))                      as state_name,
        upper(trim(city))                       as city_name,
        trim(home_locality)                     as home_locality,
        UPPER(trim(home_store_id))              as home_store_id,
        cast(is_pass_member as bool)            as is_pass_member, 
        cast(signup_date    as date)            as signup_date,

        -- derived: days since signup
        date_diff(current_date(), cast(signup_date as date), day) as days_since_signup,
        current_timestamp()                     as _dbt_loaded_at

    from source
    where customer_id is not null and email is not null
)

select * from cleaned