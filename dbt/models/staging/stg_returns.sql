with source as (select * from {{ source("raw","returns") }}),
cleaned as (
    select
        cast(return_id as string) as return_id,
        cast(order_id as string) as order_id,
        cast(product_id as string) as product_id,
        cast(return_date as date) as return_date,
        trim(reason) as return_reason,
        cast(refund_amount as numeric) as refund_amount_usd,
        current_timestamp() as _dbt_loaded_at
    from source where return_id is not null and order_id is not null)
select * from cleaned