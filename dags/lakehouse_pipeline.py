from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# 1. Applying default settings to all the tasks
default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

# 2. Defining the DAG
with DAG(
    dag_id='olist_lakehouse_pipeline',
    default_args=default_args,
    start_date=datetime(2026, 3, 10),
    schedule_interval='@daily',          # Or schedule=None
    catchup=False,
    description='Automated pipeline for Bronze ingestion and Silver/Gold dbt transformations'
) as dag:
    
    # Task 1. The Ingestion Engine
    ingest_bronze = BashOperator(
        task_id='load_bronze_layer',
        bash_command='cd /opt/airflow && python load_bronze.py'
    )

    # Task 2. The Transforamtion Engine
    transform_lakehouse = BashOperator(
        task_id='build_silver_and_gold_layers',
        bash_command='cd /opt/airflow/dbt && dotenv -f /opt/airflow/.env run -- dbt run --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt'
    )

    # 3. The Dependency Architecture
    ingest_bronze >> transform_lakehouse
