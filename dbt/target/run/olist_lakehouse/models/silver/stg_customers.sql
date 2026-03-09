
  
    

create or replace transient table OLIST_LAKEHOUSE.SILVER.stg_customers
    
    
    
    as (WITH raw_customers AS (
    SELECT
        $1::VARCHAR AS customer_id,
        $2::VARCHAR AS customer_unique_id,
        $3::VARCHAR AS customer_zip_code_prefix,
        $4::VARCHAR AS customer_city,
        $5::VARCHAR AS customer_state
    FROM @OLIST_LAKEHOUSE.BRONZE.raw_stage/olist_customers_dataset.csv.gz
    (FILE_FORMAT => 'OLIST_LAKEHOUSE.BRONZE.CSV_FORMAT')
)

SELECT * FROM raw_customers
    )
;


  