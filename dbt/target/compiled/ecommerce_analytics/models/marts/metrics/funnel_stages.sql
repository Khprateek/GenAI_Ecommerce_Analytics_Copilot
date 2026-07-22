SELECT 
        event_date, 
        device_type, 
        'Sessions' as stage_name, 
        1 as stage_order, 
        sessions as count from `genai-copilot-enterprisedata`.`metrics`.`conversion_rate`
UNION ALL
    SELECT 
        event_date, 
        device_type, 
        'Product Views', 
        2, 
        product_views from `genai-copilot-enterprisedata`.`metrics`.`conversion_rate`
UNION ALL
    SELECT 
        event_date,
        device_type,
        'Add to Cart',
        3,
        add_to_cart from `genai-copilot-enterprisedata`.`metrics`.`conversion_rate`
UNION ALL
    SELECT 
        event_date, 
        device_type, 
        'Purchases', 
        4, 
        purchases from `genai-copilot-enterprisedata`.`metrics`.`conversion_rate`