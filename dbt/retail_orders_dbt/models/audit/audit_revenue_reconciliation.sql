with bronze_order_items as (
  select
    count(*) as bronze_order_item_rows,
    round(sum(net_amount), 2) as bronze_net_amount
  from {{ source('bronze', 'ORDER_ITEMS') }}
),

gold_fact as (
  select
    count(*) as gold_fact_rows,
    round(sum(net_amount), 2) as gold_net_amount,
    round(sum(revenue_amount), 2) as gold_revenue_amount
  from {{ ref('fact_order_items') }}
)

select
  bronze_order_items.bronze_order_item_rows,
  gold_fact.gold_fact_rows,
  bronze_order_items.bronze_net_amount,
  gold_fact.gold_net_amount,
  gold_fact.gold_revenue_amount,
  round(gold_fact.gold_net_amount - bronze_order_items.bronze_net_amount, 2) as net_amount_diff,
  case
    when gold_fact.gold_fact_rows = bronze_order_items.bronze_order_item_rows
      and abs(gold_fact.gold_net_amount - bronze_order_items.bronze_net_amount) < 0.01
      then 'PASS'
    else 'FAIL'
  end as reconciliation_status
from bronze_order_items
cross join gold_fact
