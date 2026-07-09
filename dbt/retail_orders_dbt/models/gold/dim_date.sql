select distinct
  to_number(to_char(order_date, 'YYYYMMDD')) as date_key,
  order_date as date_day,
  year(order_date) as year,
  month(order_date) as month,
  monthname(order_date) as month_name,
  quarter(order_date) as quarter
from {{ ref('stg_orders') }}
