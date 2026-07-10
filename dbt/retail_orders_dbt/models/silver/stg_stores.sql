select
  store_id,
  store_name,
  channel,
  city,
  province,
  load_run_date
from {{ source('bronze', 'STORES') }}