-- Daily funnel: sessions → product views → add to cart → purchase

with events as (
    select * from {{ ref('stg_events') }}
),

daily_funnel as (
    select
        event_date,
        device_type,

        count(distinct session_id)                                          as sessions,

        count(distinct case when event_type = 'page_view'
            and page like '%product%'
            then session_id end)                                            as product_views,

        count(distinct case when event_type = 'add_to_cart'
            then session_id end)                                            as add_to_cart,

        count(distinct case when event_type = 'purchase'
            then session_id end)                                            as purchases

    from events
    group by 1, 2
),

with_rates as (
    select
        *,
        -- conversion rates
        round(safe_divide(product_views, sessions) * 100, 2)    as view_rate_pct,
        round(safe_divide(add_to_cart, sessions) * 100, 2)      as atc_rate_pct,
        round(safe_divide(purchases, sessions) * 100, 2)        as purchase_rate_pct,
        round(safe_divide(purchases, add_to_cart) * 100, 2)     as cart_conversion_pct
    from daily_funnel
)

select * from with_rates
order by event_date desc