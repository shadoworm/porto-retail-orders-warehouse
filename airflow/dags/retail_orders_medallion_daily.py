from __future__ import annotations

import os
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator


PROJECT_DIR = os.environ.get("PROJECT_DIR", "/opt/airflow/project")
RUN_DATE = "{{ ds }}"


with DAG(
    dag_id="retail_orders_medallion_daily",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["portfolio", "retail", "medallion"],
) as dag:
    start = EmptyOperator(task_id="start")

    generate_synthetic_data = BashOperator(
        task_id="generate_synthetic_data",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/retail_orders/generate_synthetic_data.py --run-date {RUN_DATE}"
        ),
    )

    upload_raw_to_s3 = BashOperator(
        task_id="upload_raw_to_s3",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python src/retail_orders/upload_to_s3.py "
            f"--local-dir data/raw/run_date={RUN_DATE} "
            "--bucket ${S3_BUCKET} "
            f"--prefix ${{S3_PREFIX}}/run_date={RUN_DATE}"
        ),
    )

    load_bronze_to_snowflake = BashOperator(
        task_id="load_bronze_to_snowflake",
        bash_command="echo TODO: run Snowflake COPY INTO commands for Bronze tables",
    )

    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command=f"cd {PROJECT_DIR}/dbt/retail_orders_dbt && DBT_PROFILES_DIR={PROJECT_DIR}/dbt dbt run",
    )

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command=f"cd {PROJECT_DIR}/dbt/retail_orders_dbt && DBT_PROFILES_DIR={PROJECT_DIR}/dbt dbt test",
    )

    publish_audit_summary = BashOperator(
        task_id="publish_audit_summary",
        bash_command="echo TODO: query Audit schema and print row-count/reconciliation summary",
    )

    notify_pipeline_status = BashOperator(
        task_id="notify_pipeline_status",
        bash_command="echo Retail orders medallion pipeline finished for run date {{ ds }}",
    )

    start >> generate_synthetic_data >> upload_raw_to_s3 >> load_bronze_to_snowflake
    load_bronze_to_snowflake >> run_dbt_models >> run_dbt_tests >> publish_audit_summary >> notify_pipeline_status
