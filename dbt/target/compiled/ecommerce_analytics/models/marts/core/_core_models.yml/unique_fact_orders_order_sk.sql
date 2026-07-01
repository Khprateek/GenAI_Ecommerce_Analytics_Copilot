
    
    

with dbt_test__target as (

  select order_sk as unique_field
  from `genai-copilot-enterprisedata`.`marts`.`fact_orders`
  where order_sk is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


