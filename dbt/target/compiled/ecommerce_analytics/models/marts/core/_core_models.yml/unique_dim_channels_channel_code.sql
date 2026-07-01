
    
    

with dbt_test__target as (

  select channel_code as unique_field
  from `genai-copilot-enterprisedata`.`marts`.`dim_channels`
  where channel_code is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


