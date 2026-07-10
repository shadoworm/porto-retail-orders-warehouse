import os

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from dotenv import load_dotenv
import snowflake.connector


st.set_page_config(page_title="Retail Orders Warehouse", layout="wide")
st.title("Retail Orders Medallion Warehouse")

st.caption("Gold star schema metrics with Audit layer evidence from Snowflake.")


load_dotenv()


def get_config_value(key: str, default: str | None = None) -> str:
    env_value = os.environ.get(key)
    if env_value:
        return env_value

    try:
        secret_value = st.secrets.get(key)
    except StreamlitSecretNotFoundError:
        secret_value = None

    if secret_value:
        return str(secret_value)

    if default is not None:
        return default

    raise RuntimeError(f"Missing required config value: {key}")


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=get_config_value("SNOWFLAKE_ACCOUNT"),
        user=get_config_value("SNOWFLAKE_USER"),
        password=get_config_value("SNOWFLAKE_PASSWORD"),
        role=get_config_value("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=get_config_value("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=get_config_value("SNOWFLAKE_DATABASE", "RETAIL_ORDERS_WH"),
    )


@st.cache_data(ttl=600)
def run_query(query: str) -> pd.DataFrame:
    with get_connection().cursor() as cursor:
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        return pd.DataFrame(cursor.fetchall(), columns=columns)


monthly_revenue = run_query(
    """
    select
      date_trunc('month', order_date) as month,
      sum(revenue_amount) as revenue,
      count(distinct order_id) as orders
    from GOLD.fact_order_items
    group by 1
    order by 1
    """
)

top_products = run_query(
    """
    select
      product.product_name,
      product.category,
      sum(fact.revenue_amount) as revenue
    from GOLD.fact_order_items fact
    join GOLD.dim_product product
      on fact.product_id = product.product_id
    group by 1, 2
    order by revenue desc
    limit 10
    """
)

store_sales = run_query(
    """
    select
      store.channel,
      store.store_name,
      sum(fact.revenue_amount) as revenue
    from GOLD.fact_order_items fact
    join GOLD.dim_store store
      on fact.store_id = store.store_id
    group by 1, 2
    order by revenue desc
    limit 15
    """
)

customer_segments = run_query(
    """
    select
      customer.customer_segment,
      sum(fact.revenue_amount) as revenue,
      count(distinct fact.customer_id) as customers
    from GOLD.fact_order_items fact
    join GOLD.dim_customer customer
      on fact.customer_id = customer.customer_id
    group by 1
    order by revenue desc
    """
)

payment_methods = run_query(
    """
    select
      payment.payment_method_name,
      sum(fact.revenue_amount) as revenue
    from GOLD.fact_order_items fact
    join GOLD.dim_payment_method payment
      on fact.payment_method = payment.payment_method
    group by 1
    order by revenue desc
    """
)

reconciliation = run_query("select * from AUDIT.audit_revenue_reconciliation")
quality_summary = run_query("select * from AUDIT.audit_quality_summary order by check_name")
row_counts = run_query("select * from AUDIT.audit_row_counts order by table_name")

total_revenue = monthly_revenue["REVENUE"].sum()
total_orders = monthly_revenue["ORDERS"].sum()
fact_rows = row_counts.loc[row_counts["TABLE_NAME"] == "gold.fact_order_items", "ROW_COUNT"].iloc[0]
reconciliation_status = reconciliation["RECONCILIATION_STATUS"].iloc[0]

metric_cols = st.columns(4)
metric_cols[0].metric("Revenue", f"IDR {total_revenue:,.0f}")
metric_cols[1].metric("Orders", f"{total_orders:,.0f}")
metric_cols[2].metric("Fact rows", f"{fact_rows:,.0f}")
metric_cols[3].metric("Audit status", reconciliation_status)

st.divider()

left, right = st.columns(2)

with left:
    fig = px.line(monthly_revenue, x="MONTH", y="REVENUE", markers=True, title="Monthly Revenue")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(top_products, x="REVENUE", y="PRODUCT_NAME", color="CATEGORY", orientation="h", title="Top Products")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.bar(store_sales, x="REVENUE", y="STORE_NAME", color="CHANNEL", orientation="h", title="Sales by Store")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    fig = px.pie(customer_segments, names="CUSTOMER_SEGMENT", values="REVENUE", title="Revenue by Customer Segment")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Payment Method Revenue")
st.dataframe(payment_methods, use_container_width=True, hide_index=True)

st.subheader("Audit Evidence")
audit_left, audit_right = st.columns(2)
audit_left.dataframe(quality_summary, use_container_width=True, hide_index=True)
audit_right.dataframe(row_counts, use_container_width=True, hide_index=True)
