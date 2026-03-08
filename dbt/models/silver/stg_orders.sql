WITH raw_orders AS (
    SELECT
        $1::VARCHAR AS order_id,
        $2::VARCHAR AS customer_id,
        $3::VARCHAR AS order_status,
        $4::TIMESTAMP AS order_purchase_timestamp,
        $5::TIMESTAMP AS order_approved_at,
        $6::TIMESTAMP AS order_delivered_carrier_date,
        $7::TIMESTAMP AS order_delivered_customer_date,
        $8::TIMESTAMP AS order_estimated_delivery_date
    FROM @OLIST_LAKEHOUSE.BRONZE.raw_stage/olist_orders_dataset.csv.gz
    (FILE_FORMAT => 'OLIST_LAKEHOUSE.BRONZE.CSV_FORMAT')
)

SELECT * FROM raw_orders