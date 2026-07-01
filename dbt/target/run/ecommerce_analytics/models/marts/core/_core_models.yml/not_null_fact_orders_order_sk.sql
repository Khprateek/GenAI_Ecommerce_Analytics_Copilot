
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_sk
from `genai-copilot-enterprisedata`.`marts`.`fact_orders`
where order_sk is null



  
  
      
    ) dbt_internal_test