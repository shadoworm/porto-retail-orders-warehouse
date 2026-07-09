# Hands-on Checklist

Use this as the implementation path. Do not add this project to `porto-alan` until the evidence is real.

## Runtime date rule

Use `run_date` as a runtime parameter:

- Manual run: pass `--run-date YYYY-MM-DD`.
- Airflow run: use `{{ ds }}` from the DAG execution date.
- `.env`: keep environment config such as bucket, prefix, and credentials. Do not rely on `.env` as the main source of `run_date` for scheduled pipelines.

## 1. Generate source data

- Run the generator script.
- Confirm output files under `data/raw/run_date=YYYY-MM-DD/`.
- Expected source files:
  - `customers.csv`
  - `products.csv`
  - `stores.csv`
  - `orders.csv`
  - `order_items.csv`
  - `payments.csv`

## 2. Land files in S3

- Create an S3 bucket or reuse a dedicated portfolio bucket.
- Upload files to `retail_orders/run_date=YYYY-MM-DD/`.
- Capture S3 evidence for the portfolio.

## 3. Create Snowflake objects

- Run `sql/snowflake/01_create_objects.sql`.
- Create schemas: `BRONZE`, `SILVER`, `GOLD`, and `AUDIT`.
- Create external/internal stage and file format.
- Load source files into Bronze tables.

## 4. Build dbt models

- Configure `dbt/profiles.yml` from `dbt/profiles.yml.example`.
- Build Silver models for cleaning, typing, standardization, and deduping.
- Build Gold star schema models.
- Add dbt tests for uniqueness, not null, relationships, accepted values, and non-negative revenue.

## 5. Orchestrate with Airflow

- Run Airflow locally with Docker Compose.
- Implement each DAG task until the full DAG succeeds:
  - generate data
  - upload raw files to S3
  - load Bronze tables
  - run dbt Silver/Gold/Audit
  - run dbt tests
  - publish audit summary

## 6. Build Streamlit dashboard

- Read from Snowflake Gold tables, not local CSV.
- Show revenue trend, top products, sales by store, customer segment, and data quality status.
- Capture dashboard screenshot for the portfolio.

## Acceptance criteria

- Airflow DAG succeeds end to end.
- S3 has run-date partitioned raw files.
- Snowflake Bronze tables load all source data.
- dbt models create Silver, Gold, and Audit tables.
- At least 10 dbt tests pass.
- `gold.fact_order_items` has a clear grain and valid joins to dimensions.
- Streamlit reads from Gold tables.
