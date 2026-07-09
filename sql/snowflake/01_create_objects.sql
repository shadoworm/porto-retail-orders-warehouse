-- Replace placeholder values before running.
create database if not exists RETAIL_ORDERS_WH;

create schema if not exists RETAIL_ORDERS_WH.BRONZE;
create schema if not exists RETAIL_ORDERS_WH.SILVER;
create schema if not exists RETAIL_ORDERS_WH.GOLD;
create schema if not exists RETAIL_ORDERS_WH.AUDIT;

create file format if not exists RETAIL_ORDERS_WH.BRONZE.CSV_WITH_HEADER
  type = csv
  field_delimiter = ','
  skip_header = 1
  field_optionally_enclosed_by = '"'
  null_if = ('', 'NULL', 'null');

-- TODO: Create an external stage for your S3 bucket.
-- create stage if not exists RETAIL_ORDERS_WH.BRONZE.S3_RETAIL_ORDERS_STAGE
--   url = 's3://your-s3-bucket-name/retail_orders/'
--   credentials = (aws_key_id = '...' aws_secret_key = '...')
--   file_format = RETAIL_ORDERS_WH.BRONZE.CSV_WITH_HEADER;

create table if not exists RETAIL_ORDERS_WH.BRONZE.CUSTOMERS (
  customer_id number,
  customer_name varchar,
  customer_segment varchar,
  city varchar,
  province varchar,
  created_at timestamp_ntz,
  load_run_date date
);

create table if not exists RETAIL_ORDERS_WH.BRONZE.PRODUCTS (
  product_id number,
  product_name varchar,
  category varchar,
  brand varchar,
  unit_cost number(18,2),
  list_price number(18,2),
  is_active boolean,
  load_run_date date
);

create table if not exists RETAIL_ORDERS_WH.BRONZE.STORES (
  store_id number,
  store_name varchar,
  channel varchar,
  city varchar,
  province varchar,
  load_run_date date
);

create table if not exists RETAIL_ORDERS_WH.BRONZE.ORDERS (
  order_id number,
  customer_id number,
  store_id number,
  order_date date,
  order_status varchar,
  created_at timestamp_ntz,
  load_run_date date
);

create table if not exists RETAIL_ORDERS_WH.BRONZE.ORDER_ITEMS (
  order_item_id number,
  order_id number,
  product_id number,
  quantity number,
  unit_price number(18,2),
  discount_amount number(18,2),
  gross_amount number(18,2),
  net_amount number(18,2),
  load_run_date date
);

create table if not exists RETAIL_ORDERS_WH.BRONZE.PAYMENTS (
  payment_id number,
  order_id number,
  payment_method varchar,
  payment_status varchar,
  paid_amount number(18,2),
  load_run_date date
);
