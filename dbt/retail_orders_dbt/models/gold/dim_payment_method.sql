select distinct
  payment_method,
  payment_method as payment_method_name
from {{ ref('stg_payments') }}