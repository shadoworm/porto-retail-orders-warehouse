import os

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Retail Orders Warehouse", layout="wide")
st.title("Retail Orders Medallion Warehouse")

st.caption("Connect this dashboard to Snowflake Gold tables after dbt models are ready.")


def load_placeholder_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "month": ["2024-01", "2024-02", "2024-03"],
            "revenue": [120_000_000, 145_000_000, 138_000_000],
        }
    )


if os.getenv("USE_PLACEHOLDER_DATA", "true").lower() == "true":
    data = load_placeholder_data()
    st.warning("Placeholder mode is on. Replace this with Snowflake Gold table queries before using portfolio evidence.")
else:
    st.info("TODO: add Snowflake query for gold.fact_order_items.")
    data = load_placeholder_data()

fig = px.line(data, x="month", y="revenue", markers=True, title="Monthly Revenue")
st.plotly_chart(fig, use_container_width=True)
