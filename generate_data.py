from faker import Faker
import pandas as pd
import random

fake = Faker()

# Config
NUM_CUSTOMERS = 20000
NUM_PRODUCTS = 5000
NUM_ORDERS = 50000
NUM_ORDER_ITEMS = 200000

# Customers
customers = []

for customer_id in range(1, NUM_CUSTOMERS +1):
        customers.append({
                "customers_id":customer_id,
                "name": fake.name(),
                "email": fake.email(),
                "country": fake.country(),
                "signup_date": fake.date_between(
                        start_date="-3y",
                        end_date="today"
                )
        })

customers_df = pd.DataFrame(customers)
customers_df.to_csv("data/customers.csv", index=False)

print("customers.csv created")

# Products 
products =[]

categories = [
        "Electronics",
        "Fashion",
        "Home",
        "Sports",
        "Books"
]

for product_id in range(1, NUM_PRODUCTS + 1):
        products.append({
                "product_id": product_id,
                "product_name":fake.word().title(),
                "category": random.choice(categories),
                "price": round(random.uniform(5,500), 2)
        })

products_df = pd.DataFrame(products)
products_df.to_csv("data/products.csv", index=False)

print("product.csv created")

# ORDERS

orders = []

statuses = [
        "Completed",
        "Pending",
        "Cancelled",
        "Returned"
]

channels = [
        "Web",
        "Mobile",
        "Store"
]

for order_id in range(1, NUM_ORDERS + 1):
        revenue = round(random.uniform(20, 1000), 2)
        discount = round(random.uniform(0, 100),2)

        orders.append({
                "order_id":order_id,
                "customer_id":random.randint(1, NUM_CUSTOMERS),
                "order_date": fake.date_between(
                        start_date = "-2y",
                        end_date = "today"
                ),
                "status": random.choice(statuses),
                "channel": random.choice(channels),
                "revenue": revenue,
                "discount": discount,
                "country": fake.country()
        })

orders_df = pd.DataFrame(orders)
orders_df.to_csv("data/orders.csv", index=False)

print("orders.csv created")

# ORDER Items

order_items = []

for item_id in range(1, NUM_ORDER_ITEMS + 1):
        qty = random.randint(1, 5)

        order_items.append({
                "order_item_id": item_id,
                "order_id": random.randint(1, NUM_ORDERS),
                "product_id": random.randint(1, NUM_PRODUCTS),
                "quantity": qty,
                "unit_price": round(random.uniform(5,500),2)
        })

order_items_df = pd.DataFrame(order_items)
order_items_df.to_csv("data/order_items.csv", index=False)

print("order_items.csv created")

# -------------------------
# EVENTS
# -------------------------
events = []

event_types = [
    "page_view",
    "add_to_cart",
    "checkout",
    "purchase"
]

for event_id in range(1, 100001):
    events.append({
        "event_id": event_id,
        "customer_id": random.randint(1, NUM_CUSTOMERS),
        "event_type": random.choice(event_types),
        "event_timestamp": fake.date_time_between(
            start_date="-1y",
            end_date="now"
        )
    })

events_df = pd.DataFrame(events)

events_df.to_csv(
    f"data/events.csv",
    index=False
)

print("events.csv created")