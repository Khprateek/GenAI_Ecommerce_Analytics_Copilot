
    
    

with dbt_test__target as (

  select customers_id as unique_field
  from `genai-copilot-enterprisedata`.`raw`.`customers`
  where customers_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


