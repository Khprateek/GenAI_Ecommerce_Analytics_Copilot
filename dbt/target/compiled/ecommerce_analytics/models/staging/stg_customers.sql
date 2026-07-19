with source as (
    select * from `genai-copilot-enterprisedata`.`raw`.`customers`
),

cleaned as (
    select
        cast(customers_id   as string)  as customer_id,
        trim(split(name, ' ')[safe_offset(0)]) as first_name,
        trim(split(name, ' ')[safe_offset(1)]) as last_name,
        lower(concat(split(email, '@')[safe_offset(0)], '_', cast(customers_id as string), '@', split(email, '@')[safe_offset(1)])) as email,
        upper(trim(state_name))            as state_name,
        upper(trim(city_name))             as city_name,

        cast(signup_date    as date)    as signup_date,
        cast(null as date)              as birth_date,

        -- derived: days since signup
        date_diff(current_date(), cast(signup_date as date), day) as days_since_signup,

        cast(null as string)            as acquisition_channel,  -- paid, organic, referral

        current_timestamp()             as _dbt_loaded_at

    from source
    where customers_id is not null and email is not null
)

select * from cleaned