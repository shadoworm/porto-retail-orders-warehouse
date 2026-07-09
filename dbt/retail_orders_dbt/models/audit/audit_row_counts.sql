select 'bronze.orders' as table_name, count(*) as row_count from {{ source('bronze', 'ORDERS') }}
union all
select 'bronze.order_items' as table_name, count(*) as row_count from {{ source('bronze', 'ORDER_ITEMS') }}
union all
select 'gold.fact_order_items' as table_name, count(*) as row_count from {{ ref('fact_order_items') }}
