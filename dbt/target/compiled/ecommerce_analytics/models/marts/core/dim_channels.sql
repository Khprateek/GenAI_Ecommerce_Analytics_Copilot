-- Static channel reference — seed-style but built in dbt
-- Add rows here as new channels are introduced

with channels as (
    select 'web' as channel_code, 'Website' as channel_name, 'Digital' as channel_type, 'Direct' as channel_category
    union all
    select 'mobile', 'Mobile App', 'Digital', 'Direct'
    union all
    select 'store', 'Physical Store', 'Offline', 'Direct'
    union all
    select 'marketplace', 'Marketplace', 'Digital', 'Partner'
    union all
    select 'social', 'Social Commerce', 'Digital', 'Partner'
    union all
    select 'email', 'Email Campaign', 'Digital', 'Marketing'
),

final as (
    select
        to_hex(md5(cast(coalesce(cast(channel_code as string), '_dbt_utils_surrogate_key_null_') as string))) as channel_sk,
        channel_code,
        channel_name,
        channel_type,
        channel_category,
        case channel_type
            when 'Digital' then true
            else false
        end as is_digital
    from channels
)

select * from final