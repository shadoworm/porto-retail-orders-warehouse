select
  payment_id,
  order_id,
  lower(payment_method) as payment_method,
  lower(payment_status) as payment_status,
  paid_amount,
  load_run_date
from {{ source('bronze', 'PAYMENTS') }}