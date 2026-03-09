
  
    

create or replace transient table OLIST_LAKEHOUSE.gold.dim_customers
    
    
    
    as (WITH stg_cutomers AS (
    SELECT * FROM OLIST_LAKEHOUSE.silver.stg_customers
)

SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM stg_customers
    )
;


  