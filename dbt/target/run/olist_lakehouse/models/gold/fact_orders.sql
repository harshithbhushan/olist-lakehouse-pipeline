
  
    

create or replace transient table OLIST_LAKEHOUSE.gold.fact_orders
    
    
    
    as (WITH stg_orders AS (
    SELECT * FROM OLIST_LAKEHOUSE.silver.stg_orders
)

SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_delivered_customer_date,
    DATEDIFF(day, order_purchase_timestamp, order_delivered_customer_date) AS delivery_time_days
FROM stg_orders
    )
;


  