with source as (
    select * from {{ source('raw', 'order_issues') }}
),

cleaned as (
    select
        cast(issue_id as string)                    as issue_id,
        cast(order_id as string)                    as order_id,
        cast(product_id as string)                  as product_id,

        cast(reported_at as timestamp)              as reported_at,
        cast(reported_at as date)                   as reported_date,

        initcap(trim(issue_type))                   as issue_type,
        initcap(trim(resolution))                   as resolution,

        cast(resolved_same_day as bool)             as resolved_same_day,
        cast(refund_amount as numeric)              as refund_amount,

        current_timestamp()                         as _dbt_loaded_at

    from source
    where issue_id is not null
)

select * from cleaned