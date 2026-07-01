
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select revenue_usd
from `genai-copilot-enterprisedata`.`marts`.`fact_orders`
where revenue_usd is null



  
  
      
    ) dbt_internal_test