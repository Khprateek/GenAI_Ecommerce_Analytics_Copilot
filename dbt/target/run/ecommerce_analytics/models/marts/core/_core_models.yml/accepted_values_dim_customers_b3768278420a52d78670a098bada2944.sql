
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        rfm_segment as value_field,
        count(*) as n_records

    from `genai-copilot-enterprisedata`.`marts`.`dim_customers`
    group by rfm_segment

)

select *
from all_values
where value_field not in (
    'Champions','Loyal Customers','New Customers','At Risk','Lost','Potential Loyalists','No Purchases'
)



  
  
      
    ) dbt_internal_test