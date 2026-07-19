"""
Generates a moderately complex e-commerce dataset for the analytics warehouse.

Tables produced:
  customers.csv        20,000 rows
  products.csv          5,000 rows  (now with brand + cost_price)
  orders.csv            50,000 rows
  order_items.csv      ~150,000 rows
  events.csv           300,000 rows
  returns.csv          ~4,000 rows  (NEW)
  marketing_spend.csv  ~2,000 rows  (NEW - daily spend by channel)

Run:  python generate_data.py
Output: ./data/*.csv
"""

import csv
import random
from pathlib import Path
from datetime import date, datetime, timedelta

from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

# Project root (directory containing this script)
BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_CUSTOMERS = 20_000
N_PRODUCTS = 5_000
N_ORDERS = 50_000
N_EVENTS = 300_000

START_DATE = date(2023, 1, 1)
END_DATE = date(2026, 8, 1)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days

CATEGORIES = {
    "Electronics": ["TechNova", "Voltix", "Quantix", "Aeroline"],
    "Apparel": ["Urban Thread", "Northwind", "Linea", "Drift Co"],
    "Home & Kitchen": ["HearthCraft", "Domora", "Nestwell", "Cookhouse"],
    "Beauty & Personal Care": ["Luma", "PureSkin", "Glowtropic", "Bareskin"],
    "Sports & Outdoors": ["PeakForm", "TrailBound", "IronGrit", "Altitude"],
    "Books": ["Penbound Press", "Inkwell", "Folio House", "Chapter & Verse"],
    "Toys & Games": ["PlayForge", "Funloop", "Brightwood", "Pixel Pals"],
}

CHANNELS = ["web", "mobile", "store", "marketplace", "social", "email"]
CHANNEL_WEIGHTS = [0.35, 0.25, 0.10, 0.15, 0.10, 0.05]

ORDER_STATUSES = ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED",
                   "CANCELLED", "PENDING", "REFUNDED"]

RETURN_REASONS = [
    "Wrong size", "Defective item", "Not as described",
    "Changed mind", "Arrived late", "Better price found elsewhere"
]


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def random_datetime(start: date, end: date) -> datetime:
    d = random_date(start, end)
    return datetime.combine(d, datetime.min.time()) + timedelta(
        hours=random.randint(0, 23), minutes=random.randint(0, 59)
    )


# ── CUSTOMERS ────────────────────────────────────────────────────────────────
print("Generating customers...")
customers = []
for i in range(1, N_CUSTOMERS + 1):
    signup = random_date(START_DATE, END_DATE)
    customers.append({
        "customers_id": f"CUST{i:06d}",
        "name": fake.name(),
        "email": fake.unique.email(),
        "country": fake.country_code(),
        "signup_date": signup.isoformat(),
    })

with open(OUT_DIR / "customers.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=customers[0].keys())
    writer.writeheader()
    writer.writerows(customers)

# ── PRODUCTS (with brand + cost_price) ──────────────────────────────────────
print("Generating products...")
products = []
product_cost_map = {}  # product_id -> cost_price, used later for margin in returns/orders
for i in range(1, N_PRODUCTS + 1):
    category = random.choice(list(CATEGORIES.keys()))
    brand = random.choice(CATEGORIES[category])
    price = round(random.uniform(8, 450), 2)
    cost_price = round(price * random.uniform(0.35, 0.65), 2)  # 35-65% COGS

    product_id = f"PROD{i:06d}"
    products.append({
        "product_id": product_id,
        "product_name": f"{brand} {fake.word().capitalize()} {fake.word().capitalize()}",
        "category": category,
        "brand": brand,
        "price": price,
        "cost_price": cost_price,
    })
    product_cost_map[product_id] = (price, cost_price)

with open(OUT_DIR / "products.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=products[0].keys())
    writer.writeheader()
    writer.writerows(products)

customer_ids = [c["customers_id"] for c in customers]
product_ids = [p["product_id"] for p in products]

# ── ORDERS + ORDER_ITEMS ────────────────────────────────────────────────────
print("Generating orders + order_items...")
orders = []
order_items = []
item_counter = 1

for i in range(1, N_ORDERS + 1):
    order_id = f"ORD{i:07d}"
    customer_id = random.choice(customer_ids)
    order_date_val = random_date(START_DATE, END_DATE)
    status = random.choice(ORDER_STATUSES)
    channel = random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0]

    n_items = random.randint(1, 5)
    chosen_products = random.sample(product_ids, n_items)

    order_revenue = 0.0
    for pid in chosen_products:
        price, _ = product_cost_map[pid]
        qty = random.randint(1, 4)
        unit_price = round(price * random.uniform(0.9, 1.05), 2)  # slight price drift
        order_items.append({
            "order_item_id": f"ITEM{item_counter:08d}",
            "order_id": order_id,
            "product_id": pid,
            "quantity": qty,
            "unit_price": unit_price,
        })
        order_revenue += qty * unit_price
        item_counter += 1

    discount = round(order_revenue * random.choice([0, 0, 0, 0.05, 0.10, 0.15]), 2)

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "order_date": order_date_val.isoformat(),
        "status": status,
        "channel": channel,
        "revenue": round(order_revenue, 2),
        "discount": discount,
    })

with open(OUT_DIR / "orders.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=orders[0].keys())
    writer.writeheader()
    writer.writerows(orders)

with open(OUT_DIR / "order_items.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=order_items[0].keys())
    writer.writeheader()
    writer.writerows(order_items)

# ── RETURNS (NEW) ────────────────────────────────────────────────────────────
print("Generating returns...")
completed_orders = [o for o in orders if o["status"] == "COMPLETED"]
return_sample = random.sample(completed_orders, k=int(len(completed_orders) * 0.08))  # 8% return rate

returns = []
for i, o in enumerate(return_sample, start=1):
    related_items = [it for it in order_items if it["order_id"] == o["order_id"]]
    if not related_items:
        continue
    item = random.choice(related_items)
    return_date_val = (
        datetime.fromisoformat(o["order_date"]) + timedelta(days=random.randint(1, 21))
    ).date()

    returns.append({
        "return_id": f"RET{i:06d}",
        "order_id": o["order_id"],
        "product_id": item["product_id"],
        "return_date": return_date_val.isoformat(),
        "reason": random.choice(RETURN_REASONS),
        "refund_amount": round(float(item["unit_price"]) * int(item["quantity"]), 2),
    })

with open(OUT_DIR / "returns.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=returns[0].keys())
    writer.writeheader()
    writer.writerows(returns)

# ── EVENTS ───────────────────────────────────────────────────────────────────
print("Generating events...")
event_types = ["page_view", "page_view", "page_view", "add_to_cart", "purchase"]
events = []
for i in range(1, N_EVENTS + 1):
    events.append({
        "event_id": f"EVT{i:08d}",
        "customer_id": random.choice(customer_ids) if random.random() > 0.15 else "",  # 15% anonymous
        "event_type": random.choice(event_types),
        "event_timestamp": random_datetime(START_DATE, END_DATE).isoformat(),
    })

with open(OUT_DIR / "events.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=events[0].keys())
    writer.writeheader()
    writer.writerows(events)

# ── MARKETING SPEND (NEW) — daily spend per channel ─────────────────────────
print("Generating marketing_spend...")
marketing_spend = []
spend_id = 1
current = START_DATE
base_spend = {
    "web": 800, "mobile": 600, "store": 0,
    "marketplace": 400, "social": 500, "email": 100
}
while current <= END_DATE:
    for channel, base in base_spend.items():
        if base == 0:
            continue
        spend = round(base * random.uniform(0.6, 1.4), 2)
        clicks = random.randint(200, 3000)
        impressions = clicks * random.randint(8, 25)
        marketing_spend.append({
            "spend_id": f"MKT{spend_id:07d}",
            "date": current.isoformat(),
            "channel": channel,
            "spend_usd": spend,
            "impressions": impressions,
            "clicks": clicks,
        })
        spend_id += 1
    current += timedelta(days=1)

with open(OUT_DIR / "marketing_spend.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=marketing_spend[0].keys())
    writer.writeheader()
    writer.writerows(marketing_spend)

print(f"\nDone. Files written to: {OUT_DIR}")
print(f"  customers.csv        {len(customers):>7,} rows")
print(f"  products.csv         {len(products):>7,} rows")
print(f"  orders.csv           {len(orders):>7,} rows")
print(f"  order_items.csv      {len(order_items):>7,} rows")
print(f"  returns.csv          {len(returns):>7,} rows")
print(f"  events.csv           {len(events):>7,} rows")
print(f"  marketing_spend.csv  {len(marketing_spend):>7,} rows")