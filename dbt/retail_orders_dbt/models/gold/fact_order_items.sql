select
  item.order_item_id,
  item.order_id,
  orders.customer_id,
  item.product_id,
  orders.store_id,
  payments.payment_method,
  to_number(to_char(orders.order_date, 'YYYYMMDD')) as date_key,
  orders.order_date,
  orders.order_status,
  item.quantity,
  item.unit_price,
  item.discount_amount,
  item.gross_amount,
  item.net_amount,
  greatest(item.net_amount, 0) as revenue_amount,
  item.load_run_date
from {{ ref('stg_order_items') }} item
join {{ ref('stg_orders') }} orders
  on item.order_id = orders.order_id
left join {{ ref('stg_payments') }} payments
  on item.order_id = payments.order_id
