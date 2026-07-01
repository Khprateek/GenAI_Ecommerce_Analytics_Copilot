
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select channel_code
from `genai-copilot-enterprisedata`.`marts`.`dim_channels`
where channel_code is null



  
  
      
    ) dbt_internal_test