
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customers_id
from `genai-copilot-enterprisedata`.`raw`.`customers`
where customers_id is null



  
  
      
    ) dbt_internal_test