
  
    

create or replace transient table OLIST_LAKEHOUSE.gold.dim_products
    
    
    
    as (WITH stg_products AS (
    SELECT * FROM OLIST_LAKEHOUSE.silver.stg_products
)

SELECT
    product_id,
    product_category_name,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM stg_products
    )
;


  