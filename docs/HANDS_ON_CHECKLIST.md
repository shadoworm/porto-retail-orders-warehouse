# Hands-on Checklist

Use this as the implementation path. Do not add this project to `porto-alan` until the evidence is real.

## Runtime date rule

Use `run_date` as a runtime parameter:

- Manual run: pass `--run-date YYYY-MM-DD`.
- Airflow run: use `{{ ds }}` from the DAG execution date.
- `.env`: keep environment config such as bucket, prefix, and credentials. Do not rely on `.env` as the main source of `run_date` for scheduled pipelines.

Set a PowerShell variable for manual work:

```powershell
cd D:\Project\porto-retail-orders-warehouse
.\scripts\load_env.ps1
$RUN_DATE = "2026-07-10"
```

## 1. Generate source data

From the project root:

```powershell
cd D:\Project\porto-retail-orders-warehouse
.\.venv\Scripts\Activate.ps1
python src\retail_orders\generate_synthetic_data.py --run-date $RUN_DATE
```

Confirm output files:

```powershell
Get-ChildItem "data\raw\run_date=$RUN_DATE" -File | Select-Object Name,Length
```

Expected output files:

- `customers.csv`
- `products.csv`
- `stores.csv`
- `orders.csv`
- `order_items.csv`
- `payments.csv`

## 2. Land files in S3

Create a dedicated bucket if needed:

```powershell
aws s3api create-bucket `
  --bucket alan-retail-orders-raw-743107202800-20260710 `
  --region ap-southeast-1 `
  --create-bucket-configuration LocationConstraint=ap-southeast-1

aws s3api put-public-access-block `
  --bucket alan-retail-orders-raw-743107202800-20260710 `
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

Upload files:

```powershell
python src\retail_orders\upload_to_s3.py `
  --local-dir "data\raw\run_date=$RUN_DATE" `
  --bucket alan-retail-orders-raw-743107202800-20260710 `
  --prefix "retail_orders/run_date=$RUN_DATE"
```

Verify S3 objects with AWS CLI:

```powershell
aws s3 ls "s3://alan-retail-orders-raw-743107202800-20260710/retail_orders/run_date=$RUN_DATE/"
```

If AWS CLI is not installed, verify with Python:

```powershell
@"
import boto3

bucket = "alan-retail-orders-raw-743107202800-20260710"
prefix = "retail_orders/run_date=$RUN_DATE/"

resp = boto3.client("s3").list_objects_v2(Bucket=bucket, Prefix=prefix)
for obj in resp.get("Contents", []):
    print(obj["Key"], obj["Size"])
print("object_count=", resp.get("KeyCount", 0))
"@ | python -
```

## 3. Create Snowflake objects

Run the setup SQL in a Snowflake worksheet:

```sql
-- Open and run:
-- sql/snowflake/01_create_objects.sql
```

Create a Snowflake storage integration for S3. Use AWS IAM Role trust policy with the Snowflake `STORAGE_AWS_IAM_USER_ARN` and `STORAGE_AWS_EXTERNAL_ID` returned by `desc integration`.

```sql
create or replace storage integration S3_RETAIL_ORDERS_INTEGRATION
  type = external_stage
  storage_provider = 'S3'
  enabled = true
  storage_aws_role_arn = 'arn:aws:iam::<AWS_ACCOUNT_ID>:role/snowflake-retail-orders-s3-role'
  storage_allowed_locations = ('s3://alan-retail-orders-raw-743107202800-20260710/retail_orders/');

desc integration S3_RETAIL_ORDERS_INTEGRATION;
```

Create the external stage:

```sql
create or replace stage RETAIL_ORDERS_WH.BRONZE.S3_RETAIL_ORDERS_STAGE
  url = 's3://alan-retail-orders-raw-743107202800-20260710/retail_orders/'
  storage_integration = S3_RETAIL_ORDERS_INTEGRATION
  file_format = RETAIL_ORDERS_WH.BRONZE.CSV_WITH_HEADER;

list @RETAIL_ORDERS_WH.BRONZE.S3_RETAIL_ORDERS_STAGE;
```

Load one Bronze table first to validate the pattern:

```sql
copy into RETAIL_ORDERS_WH.BRONZE.ORDERS
from (
  select
    $1::number,
    $2::number,
    $3::number,
    $4::date,
    $5::varchar,
    $6::timestamp_ntz,
    to_date('2026-07-10')
  from @RETAIL_ORDERS_WH.BRONZE.S3_RETAIL_ORDERS_STAGE/run_date=2026-07-10/orders.csv
)
file_format = RETAIL_ORDERS_WH.BRONZE.CSV_WITH_HEADER;
```

After it works, repeat the `copy into` pattern for `customers`, `products`, `stores`, `order_items`, and `payments`.

Verify Bronze row counts:

```sql
select 'CUSTOMERS' as table_name, count(*) as row_count from RETAIL_ORDERS_WH.BRONZE.CUSTOMERS
union all
select 'PRODUCTS', count(*) from RETAIL_ORDERS_WH.BRONZE.PRODUCTS
union all
select 'STORES', count(*) from RETAIL_ORDERS_WH.BRONZE.STORES
union all
select 'ORDERS', count(*) from RETAIL_ORDERS_WH.BRONZE.ORDERS
union all
select 'ORDER_ITEMS', count(*) from RETAIL_ORDERS_WH.BRONZE.ORDER_ITEMS
union all
select 'PAYMENTS', count(*) from RETAIL_ORDERS_WH.BRONZE.PAYMENTS;
```

## 4. Build dbt models

Copy dbt profile template:

```powershell
Copy-Item dbt\profiles.yml.example dbt\profiles.yml
```

Load `.env`, then test dbt connection:

```powershell
cd D:\Project\porto-retail-orders-warehouse
.\scripts\load_env.ps1
dbt debug --project-dir dbt\retail_orders_dbt --profiles-dir dbt
```

Run models and tests:

```powershell
dbt run
dbt test
```

Build Silver first while learning:

```powershell
dbt run --select silver
dbt test --select silver
```

Then build Gold and Audit:

```powershell
dbt run --select gold audit
dbt test --select gold
```

Gold star schema:

- Fact table: `fact_order_items`
- Grain: one row per order item
- Dimensions: `dim_customer`, `dim_product`, `dim_store`, `dim_date`, and `dim_payment_method`
- Relationship tests should validate that fact foreign keys match the dimension keys.

Build and test Audit models:

```powershell
dbt run --select audit
dbt test --select audit
```

Audit evidence tables:

- `audit_row_counts`: Bronze and Gold row counts.
- `audit_revenue_reconciliation`: Bronze order item net amount vs Gold fact net amount.
- `audit_quality_summary`: null, duplicate, and negative revenue checks.

## 5. Orchestrate with Airflow

Start Airflow locally:

```powershell
cd D:\Project\porto-retail-orders-warehouse
docker compose up
```

Open Airflow:

```text
http://localhost:8080
username: admin
password: admin
```

Trigger DAG:

```text
retail_orders_medallion_daily
```

Implement each DAG task until the full DAG succeeds:

- `generate_synthetic_data`
- `upload_raw_to_s3`
- `load_bronze_to_snowflake`
- `run_dbt_models`
- `run_dbt_tests`
- `publish_audit_summary`

## 6. Build Streamlit dashboard

Run the current starter app:

```powershell
cd D:\Project\porto-retail-orders-warehouse
.\scripts\load_env.ps1
streamlit run streamlit_app\app.py
```

Dashboard queries:

- Business metrics come from `GOLD.fact_order_items` and Gold dimensions.
- Quality evidence comes from `AUDIT.audit_revenue_reconciliation`, `AUDIT.audit_quality_summary`, and `AUDIT.audit_row_counts`.
- Capture dashboard screenshot for the portfolio.

## Acceptance criteria

- Airflow DAG succeeds end to end.
- S3 has run-date partitioned raw files.
- Snowflake Bronze tables load all source data.
- dbt models create Silver, Gold, and Audit tables.
- At least 10 dbt tests pass.
- `gold.fact_order_items` has a clear grain and valid joins to dimensions.
- Streamlit reads from Gold tables.
