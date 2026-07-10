# Streamlit Deployment Guide

Use Streamlit Community Cloud to publish the dashboard from this repository.

Live dashboard: https://porto-retail-orders-wh.streamlit.app/

## Recommended security setup

Create a read-only Snowflake role and user for the deployed dashboard. Do not use `ACCOUNTADMIN` in public deployments.

Run this in Snowflake and replace the password:

```sql
use role ACCOUNTADMIN;

create role if not exists RETAIL_DASHBOARD_ROLE;

grant usage on database RETAIL_ORDERS_WH to role RETAIL_DASHBOARD_ROLE;
grant usage on schema RETAIL_ORDERS_WH.GOLD to role RETAIL_DASHBOARD_ROLE;
grant usage on schema RETAIL_ORDERS_WH.AUDIT to role RETAIL_DASHBOARD_ROLE;
grant select on all tables in schema RETAIL_ORDERS_WH.GOLD to role RETAIL_DASHBOARD_ROLE;
grant select on all tables in schema RETAIL_ORDERS_WH.AUDIT to role RETAIL_DASHBOARD_ROLE;
grant select on future tables in schema RETAIL_ORDERS_WH.GOLD to role RETAIL_DASHBOARD_ROLE;
grant select on future tables in schema RETAIL_ORDERS_WH.AUDIT to role RETAIL_DASHBOARD_ROLE;
grant usage on warehouse COMPUTE_WH to role RETAIL_DASHBOARD_ROLE;

create user if not exists RETAIL_DASHBOARD_USER
  password = '<STRONG_PASSWORD>'
  default_role = RETAIL_DASHBOARD_ROLE
  default_warehouse = COMPUTE_WH
  must_change_password = false;

grant role RETAIL_DASHBOARD_ROLE to user RETAIL_DASHBOARD_USER;
```

## Deploy app

1. Open Streamlit Community Cloud.
2. Create a new app from GitHub.
3. Select:
   - Repository: `shadoworm/porto-retail-orders-warehouse`
   - Branch: `main`
   - Main file path: `streamlit_app/app.py`
4. Open advanced settings and add secrets.

Use this secrets format:

```toml
SNOWFLAKE_ACCOUNT = "your_account_identifier"
SNOWFLAKE_USER = "RETAIL_DASHBOARD_USER"
SNOWFLAKE_PASSWORD = "your_password"
SNOWFLAKE_ROLE = "RETAIL_DASHBOARD_ROLE"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "RETAIL_ORDERS_WH"
```

## Verify after deploy

The app should show:

- Revenue, orders, fact rows, and audit status metrics.
- Monthly revenue from `GOLD.fact_order_items`.
- Product, store, customer segment, and payment method views.
- Audit evidence from `AUDIT.audit_revenue_reconciliation`, `AUDIT.audit_quality_summary`, and `AUDIT.audit_row_counts`.

Use the deployed URL as the portfolio demo link after the dashboard renders successfully.

Current deployed URL:

```text
https://porto-retail-orders-wh.streamlit.app/
```
