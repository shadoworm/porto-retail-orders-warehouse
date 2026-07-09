select
  order_item_id,
  order_id,
  product_id,
  quantity,
  unit_price,
  discount_amount,
  gross_amount,
  net_amount,
  load_run_date
from {{ source('bronze', 'ORDER_ITEMS') }}
