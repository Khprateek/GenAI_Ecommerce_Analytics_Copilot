
  
    

    create or replace table `genai-copilot-enterprisedata`.`marts`.`dim_date`
      
    
    

    
    OPTIONS()
    as (
      -- Date dimension: generates one row per day from start_date to today + 1 year
-- Uses BigQuery's GENERATE_DATE_ARRAY

with date_spine as (
    select date_val
    from unnest(
        generate_date_array(
            '2022-01-01',
            date_add(current_date(), interval 365 day),
            interval 1 day
        )
    ) as date_val
),

enriched as (
    select
        -- surrogate key
        cast(format_date('%Y%m%d', date_val) as integer)  as date_key,
        date_val                                           as full_date,

        -- year / quarter / month
        extract(year     from date_val)                    as year,
        extract(quarter  from date_val)                    as quarter_number,
        concat('Q', extract(quarter from date_val))        as quarter_name,
        extract(month    from date_val)                    as month_number,
        format_date('%B', date_val)                        as month_name,
        format_date('%b', date_val)                        as month_short,

        -- week
        extract(isoweek  from date_val)                    as iso_week_number,
        extract(dayofweek from date_val)                   as day_of_week,   -- 1=Sun
        format_date('%A', date_val)                        as day_name,
        format_date('%a', date_val)                        as day_short,

        -- day
        extract(day      from date_val)                    as day_of_month,
        extract(dayofyear from date_val)                   as day_of_year,

        -- flags
        case extract(dayofweek from date_val)
            when 1 then true when 7 then true else false
        end                                                as is_weekend,

        -- fiscal (assuming Jan fiscal year start — adjust if needed)
        extract(year from date_val)                        as fiscal_year,
        extract(quarter from date_val)                     as fiscal_quarter,

        -- period labels useful for dashboard filters
        format_date('%Y-%m', date_val)                     as year_month,
        format_date('%G-W%V', date_val)                    as year_week

    from date_spine
)

select * from enriched
    );
  