with checks as (
  select
    'fact_order_items_missing_customer' as check_name,
    count(*) as issue_count
  from {{ ref('fact_order_items') }}
  where customer_id is null

  union all

  select
    'fact_order_items_missing_product' as check_name,
    count(*) as issue_count
  from {{ ref('fact_order_items') }}
  where product_id is null

  union all

  select
    'fact_order_items_missing_store' as check_name,
    count(*) as issue_count
  from {{ ref('fact_order_items') }}
  where store_id is null

  union all

  select
    'fact_order_items_missing_payment_method' as check_name,
    count(*) as issue_count
  from {{ ref('fact_order_items') }}
  where payment_method is null

  union all

  select
    'fact_order_items_negative_revenue' as check_name,
    count(*) as issue_count
  from {{ ref('fact_order_items') }}
  where revenue_amount < 0

  union all

  select
    'duplicate_order_item_id' as check_name,
    count(*) - count(distinct order_item_id) as issue_count
  from {{ ref('fact_order_items') }}
)

select
  check_name,
  issue_count,
  case when issue_count = 0 then 'PASS' else 'FAIL' end as status
from checks
