select
  customer_id,
  customer_name,
  customer_segment,
  city,
  province,
  created_at,
  load_run_date
from {{ source('bronze', 'CUSTOMERS') }}