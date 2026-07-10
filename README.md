# 50,000 Synthetic Retail Orders Orchestrated into Snowflake Medallion Warehouse

Portfolio project for practicing a modern Data Engineering workflow using synthetic retail data, AWS S3, Snowflake, Airflow, dbt, medallion architecture, and Streamlit.

This repository is intentionally built as a hands-on project. The scaffold gives the shape, naming, and guardrails. The important implementation steps are meant to be completed, tested, and documented as evidence.

## Goal

Build an end-to-end batch pipeline:

`Airflow DAG -> synthetic data generation -> S3 raw landing -> Snowflake Bronze -> dbt Silver -> dbt Gold star schema -> Audit checks -> Streamlit dashboard`

## Target Stack

- Data generation: Python, Faker, pandas
- Cloud landing: AWS S3
- Warehouse: Snowflake
- Transformation: dbt Core, dbt Snowflake
- Orchestration: Apache Airflow, Docker Compose
- Quality: dbt tests, audit SQL models
- Visualization: Streamlit, Plotly

## Target Dataset

- 50,000 orders
- 1,000 customers
- 500 products
- 25 stores
- Date range: 2024-01-01 to 2025-12-31

## Warehouse Pattern

- Bronze: raw loaded source tables from S3
- Silver: cleaned, typed, deduped, standardized models
- Gold: BI-ready star schema
- Audit: quality evidence, reconciliation, freshness, and row-count checks

Gold star schema target:

- `gold.fact_order_items`
- `gold.dim_customer`
- `gold.dim_product`
- `gold.dim_store`
- `gold.dim_date`
- `gold.dim_payment_method`

## Quick Start

1. Create a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy environment variables.

```powershell
Copy-Item .env.example .env
```

3. Load environment variables into the current PowerShell session.

```powershell
.\scripts\load_env.ps1
```

4. Choose a runtime date.

`run_date` is a pipeline parameter, not a fixed environment setting. For manual runs, pass it through the CLI. In Airflow, use the DAG execution date with `{{ ds }}`.

5. Generate local synthetic data.

```powershell
python src\retail_orders\generate_synthetic_data.py --run-date 2026-07-10
```

6. Upload raw files to S3.

```powershell
python src\retail_orders\upload_to_s3.py `
  --local-dir data\raw\run_date=2026-07-10 `
  --bucket your-s3-bucket-name `
  --prefix retail_orders/run_date=2026-07-10
```

7. Follow the implementation checklist in [docs/HANDS_ON_CHECKLIST.md](docs/HANDS_ON_CHECKLIST.md).

## Portfolio Evidence To Capture

- Airflow DAG success screenshot
- S3 landing path screenshot
- Snowflake Bronze/Silver/Gold table row counts
- dbt run and dbt test result
- Streamlit dashboard screenshot
- Final GitHub repository link under `shadoworm`
