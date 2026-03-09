WITH raw_products AS (
    SELECT
        $1::VARCHAR AS product_id,
        $2::VARCHAR AS product_category_name,
        $3::INTEGER AS product_name_length,
        $4::INTEGER AS product_description_length,
        $5::INTEGER AS product_photos_qty,
        $6::INTEGER AS product_weight_g,
        $7::INTEGER AS product_length_cm,
        $8::INTEGER AS product_height_cm,
        $9::INTEGER AS product_width_cm
    FROM @OLIST_LAKEHOUSE.BRONZE.raw_stage/olist_products_dataset.csv.gz
    (FILE_FORMAT => 'OLIST_LAKEHOUSE.BRONZE.CSV_FORMAT')
)

SELECT * FROM raw_products