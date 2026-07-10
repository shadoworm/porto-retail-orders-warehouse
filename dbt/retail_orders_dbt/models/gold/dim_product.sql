select
  product_id,
  product_name,
  category,
  brand,
  unit_cost,
  list_price,
  is_active,
  load_run_date
from {{ ref('stg_products') }}