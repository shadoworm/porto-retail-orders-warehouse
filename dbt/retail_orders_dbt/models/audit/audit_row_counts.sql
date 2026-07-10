select 'bronze.customers' as table_name, count(*) as row_count from {{ source('bronze', 'CUSTOMERS') }}
union all
select 'bronze.products' as table_name, count(*) as row_count from {{ source('bronze', 'PRODUCTS') }}
union all
select 'bronze.stores' as table_name, count(*) as row_count from {{ source('bronze', 'STORES') }}
union all
select 'bronze.orders' as table_name, count(*) as row_count from {{ source('bronze', 'ORDERS') }}
union all
select 'bronze.order_items' as table_name, count(*) as row_count from {{ source('bronze', 'ORDER_ITEMS') }}
union all
select 'bronze.payments' as table_name, count(*) as row_count from {{ source('bronze', 'PAYMENTS') }}
union all
select 'gold.dim_customer' as table_name, count(*) as row_count from {{ ref('dim_customer') }}
union all
select 'gold.dim_product' as table_name, count(*) as row_count from {{ ref('dim_product') }}
union all
select 'gold.dim_store' as table_name, count(*) as row_count from {{ ref('dim_store') }}
union all
select 'gold.dim_date' as table_name, count(*) as row_count from {{ ref('dim_date') }}
union all
select 'gold.dim_payment_method' as table_name, count(*) as row_count from {{ ref('dim_payment_method') }}
union all
select 'gold.fact_order_items' as table_name, count(*) as row_count from {{ ref('fact_order_items') }}
