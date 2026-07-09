from __future__ import annotations

import argparse
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


fake = Faker("id_ID")
random.seed(42)
Faker.seed(42)


def random_date(start: date, end: date) -> date:
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def build_customers(count: int) -> pd.DataFrame:
    segments = ["Consumer", "Corporate", "Small Business"]
    rows = []
    for customer_id in range(1, count + 1):
        rows.append(
            {
                "customer_id": customer_id,
                "customer_name": fake.name(),
                "customer_segment": random.choice(segments),
                "city": fake.city(),
                "province": fake.state(),
                "created_at": fake.date_between(start_date="-4y", end_date="-1y").isoformat(),
            }
        )
    return pd.DataFrame(rows)


def build_products(count: int) -> pd.DataFrame:
    categories = {
        "Electronics": ["Headphone", "Keyboard", "Mouse", "Monitor", "Webcam"],
        "Home": ["Lamp", "Chair", "Storage Box", "Cookware", "Bedsheet"],
        "Office": ["Notebook", "Pen Set", "Desk Organizer", "Paper", "Folder"],
        "Fashion": ["T-Shirt", "Jacket", "Sneakers", "Backpack", "Cap"],
        "Groceries": ["Coffee", "Tea", "Snack", "Rice", "Cooking Oil"],
    }
    rows = []
    for product_id in range(1, count + 1):
        category = random.choice(list(categories.keys()))
        item = random.choice(categories[category])
        rows.append(
            {
                "product_id": product_id,
                "product_name": f"{fake.color_name()} {item}",
                "category": category,
                "brand": fake.company(),
                "unit_cost": round(random.uniform(10_000, 750_000), 2),
                "list_price": round(random.uniform(25_000, 1_500_000), 2),
                "is_active": random.choice([True, True, True, False]),
            }
        )
    return pd.DataFrame(rows)


def build_stores(count: int) -> pd.DataFrame:
    channels = ["Online", "Retail Store", "Marketplace"]
    rows = []
    for store_id in range(1, count + 1):
        rows.append(
            {
                "store_id": store_id,
                "store_name": f"{fake.city()} {random.choice(['Central', 'Hub', 'Outlet'])}",
                "channel": random.choice(channels),
                "city": fake.city(),
                "province": fake.state(),
            }
        )
    return pd.DataFrame(rows)


def build_orders(order_count: int, customer_count: int, store_count: int) -> pd.DataFrame:
    statuses = ["completed", "completed", "completed", "cancelled", "returned"]
    start = date(2024, 1, 1)
    end = date(2025, 12, 31)
    rows = []
    for order_id in range(1, order_count + 1):
        order_date = random_date(start, end)
        rows.append(
            {
                "order_id": order_id,
                "customer_id": random.randint(1, customer_count),
                "store_id": random.randint(1, store_count),
                "order_date": order_date.isoformat(),
                "order_status": random.choice(statuses),
                "created_at": datetime.combine(order_date, datetime.min.time()).isoformat(),
            }
        )
    return pd.DataFrame(rows)


def build_order_items(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    product_lookup = products.set_index("product_id")["list_price"].to_dict()
    rows = []
    item_id = 1
    for order_id in orders["order_id"]:
        for _ in range(random.randint(1, 5)):
            product_id = random.randint(1, len(products))
            quantity = random.randint(1, 4)
            unit_price = round(product_lookup[product_id] * random.uniform(0.85, 1.05), 2)
            discount_amount = round(unit_price * quantity * random.choice([0, 0, 0.05, 0.1]), 2)
            rows.append(
                {
                    "order_item_id": item_id,
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_amount": discount_amount,
                    "gross_amount": round(unit_price * quantity, 2),
                    "net_amount": round((unit_price * quantity) - discount_amount, 2),
                }
            )
            item_id += 1
    return pd.DataFrame(rows)


def build_payments(orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    methods = ["credit_card", "bank_transfer", "ewallet", "cash_on_delivery"]
    totals = order_items.groupby("order_id", as_index=False)["net_amount"].sum()
    rows = []
    for index, row in totals.iterrows():
        rows.append(
            {
                "payment_id": index + 1,
                "order_id": int(row["order_id"]),
                "payment_method": random.choice(methods),
                "payment_status": "paid",
                "paid_amount": round(float(row["net_amount"]), 2),
            }
        )
    cancelled_order_ids = set(orders.loc[orders["order_status"] == "cancelled", "order_id"])
    for record in rows:
        if record["order_id"] in cancelled_order_ids:
            record["payment_status"] = "voided"
            record["paid_amount"] = 0
    return pd.DataFrame(rows)


def write_outputs(output_dir: Path, order_count: int, customer_count: int, product_count: int, store_count: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    customers = build_customers(customer_count)
    products = build_products(product_count)
    stores = build_stores(store_count)
    orders = build_orders(order_count, customer_count, store_count)
    order_items = build_order_items(orders, products)
    payments = build_payments(orders, order_items)

    datasets = {
        "customers": customers,
        "products": products,
        "stores": stores,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
    }
    for name, dataframe in datasets.items():
        dataframe.to_csv(output_dir / f"{name}.csv", index=False)
        print(f"Wrote {len(dataframe):,} rows -> {output_dir / f'{name}.csv'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-date", default=date.today().isoformat())
    parser.add_argument("--output-root", default="data/raw")
    parser.add_argument("--orders", type=int, default=50_000)
    parser.add_argument("--customers", type=int, default=1_000)
    parser.add_argument("--products", type=int, default=500)
    parser.add_argument("--stores", type=int, default=25)
    args = parser.parse_args()

    output_dir = Path(args.output_root) / f"run_date={args.run_date}"
    write_outputs(output_dir, args.orders, args.customers, args.products, args.stores)


if __name__ == "__main__":
    main()
