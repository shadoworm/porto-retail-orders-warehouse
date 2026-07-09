select
  order_id,
  customer_id,
  store_id,
  order_date,
  lower(order_status) as order_status,
  created_at,
  load_run_date
from {{ source('bronze', 'ORDERS') }}
