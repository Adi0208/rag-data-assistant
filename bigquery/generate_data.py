"""
generate_data.py
Generates realistic e-commerce sample data and saves as CSV files.
Run this locally before uploading to BigQuery.

Usage:
    python generate_data.py

Output:
    data/customers.csv
    data/products.csv
    data/orders.csv
    data/order_items.csv
    data/reviews.csv
"""

import csv
import random
import uuid
from datetime import date, timedelta
from pathlib import Path

# ── Config ───────────────────────────────────────────────────
random.seed(42)
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

NUM_CUSTOMERS = 500
NUM_PRODUCTS  = 80
NUM_ORDERS    = 2000

# ── Helpers ───────────────────────────────────────────────────
def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def uid() -> str:
    return str(uuid.uuid4())[:8].upper()

# ── Reference Data ────────────────────────────────────────────
FIRST_NAMES = ["Aditya", "Priya", "Rohan", "Sneha", "Arjun", "Neha", "Vikram",
               "Ananya", "Rahul", "Pooja", "Karan", "Divya", "Amit", "Riya",
               "Sanjay", "Meera", "Suresh", "Kavya", "Manish", "Tanya"]

LAST_NAMES = ["Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Mehta",
              "Joshi", "Nair", "Reddy", "Iyer", "Das", "Chopra", "Banerjee"]

CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
          "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat"]

SEGMENTS = ["Premium", "Regular", "At-Risk"]
SEG_WEIGHTS = [0.2, 0.6, 0.2]

CATEGORIES = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Tablet", "Smartwatch", "Camera"],
    "Clothing":    ["T-Shirt", "Jeans", "Kurta", "Jacket", "Saree", "Sneakers"],
    "Home":        ["Cookware Set", "Bedsheet", "Table Lamp", "Air Purifier", "Curtains"],
    "Sports":      ["Yoga Mat", "Dumbbells", "Cricket Bat", "Running Shoes", "Cycle"],
}

SUPPLIERS = ["TechWorld Pvt Ltd", "FashionHub", "HomeEssentials Co", "SportZone India"]

PAYMENT_METHODS = ["Credit Card", "UPI", "Net Banking", "Wallet"]
ORDER_STATUSES  = ["Completed", "Completed", "Completed", "Returned", "Cancelled", "Pending"]

REVIEW_TEXTS = {
    5: ["Absolutely love it! Best purchase ever.", "Exceeded my expectations completely.",
        "Top quality product, fast delivery.", "Perfect fit and great build quality."],
    4: ["Very good product, minor packaging issue.", "Works as described, happy with it.",
        "Good value for money.", "Solid product, would recommend."],
    3: ["Average product, nothing special.", "Okay for the price.", "Decent quality.",
        "Gets the job done but could be better."],
    2: ["Disappointed with the quality.", "Not as described, expected better.",
        "Okay but overpriced.", "Had some issues out of the box."],
    1: ["Very poor quality, not recommended.", "Broke after one week.",
        "Terrible customer support.", "Complete waste of money."],
}

# ── Generate Customers ────────────────────────────────────────
print("Generating customers...")
customers = []
for _ in range(NUM_CUSTOMERS):
    seg = random.choices(SEGMENTS, SEG_WEIGHTS)[0]
    ltv = round(random.uniform(500, 5000) if seg == "Premium"
                else random.uniform(100, 2000) if seg == "Regular"
                else random.uniform(50, 500), 2)
    customers.append({
        "customer_id":    f"CUST-{uid()}",
        "first_name":     random.choice(FIRST_NAMES),
        "last_name":      random.choice(LAST_NAMES),
        "email":          f"user{random.randint(100,9999)}@email.com",
        "city":           random.choice(CITIES),
        "country":        "India",
        "signup_date":    random_date(date(2021, 1, 1), date(2024, 6, 30)),
        "segment":        seg,
        "lifetime_value": ltv,
    })

# ── Generate Products ─────────────────────────────────────────
print("Generating products...")
products = []
suppliers_map = {"Electronics": SUPPLIERS[0], "Clothing": SUPPLIERS[1],
                 "Home": SUPPLIERS[2], "Sports": SUPPLIERS[3]}
price_ranges = {"Electronics": (999, 79999), "Clothing": (299, 4999),
                "Home": (499, 9999), "Sports": (299, 7999)}

for _ in range(NUM_PRODUCTS):
    cat  = random.choice(list(CATEGORIES.keys()))
    name = random.choice(CATEGORIES[cat])
    lo, hi = price_ranges[cat]
    price = round(random.uniform(lo, hi), 2)
    products.append({
        "product_id":     f"PROD-{uid()}",
        "product_name":   name,
        "category":       cat,
        "subcategory":    cat,
        "unit_price":     price,
        "cost_price":     round(price * random.uniform(0.4, 0.7), 2),
        "stock_quantity": random.randint(0, 500),
        "supplier":       suppliers_map[cat],
    })

# ── Generate Orders & Order Items ─────────────────────────────
print("Generating orders and order items...")
orders, order_items = [], []

for _ in range(NUM_ORDERS):
    customer  = random.choice(customers)
    order_id  = f"ORD-{uid()}"
    order_date = random_date(date(2022, 1, 1), date(2024, 12, 31))
    status    = random.choice(ORDER_STATUSES)
    num_items = random.randint(1, 5)
    chosen    = random.sample(products, num_items)
    discount  = round(random.choice([0, 0, 0, 50, 100, 200, 500]), 2)

    total = 0
    for prod in chosen:
        qty   = random.randint(1, 3)
        price = prod["unit_price"]
        item_total = round(qty * price, 2)
        total += item_total
        order_items.append({
            "item_id":    f"ITEM-{uid()}",
            "order_id":   order_id,
            "product_id": prod["product_id"],
            "quantity":   qty,
            "unit_price": price,
            "total_price": item_total,
        })

    orders.append({
        "order_id":        order_id,
        "customer_id":     customer["customer_id"],
        "order_date":      order_date,
        "status":          status,
        "total_amount":    round(max(total - discount, 0), 2),
        "discount_applied": discount,
        "shipping_city":   customer["city"],
        "shipping_country": "India",
        "payment_method":  random.choice(PAYMENT_METHODS),
    })

# ── Generate Reviews ──────────────────────────────────────────
print("Generating reviews...")
reviews = []
for _ in range(800):
    rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
    prod   = random.choice(products)
    cust   = random.choice(customers)
    reviews.append({
        "review_id":    f"REV-{uid()}",
        "product_id":   prod["product_id"],
        "customer_id":  cust["customer_id"],
        "rating":       rating,
        "review_text":  random.choice(REVIEW_TEXTS[rating]),
        "review_date":  random_date(date(2022, 6, 1), date(2024, 12, 31)),
        "helpful_votes": random.randint(0, 50),
    })

# ── Write CSV Files ───────────────────────────────────────────
datasets = {
    "customers":   customers,
    "products":    products,
    "orders":      orders,
    "order_items": order_items,
    "reviews":     reviews,
}

for name, rows in datasets.items():
    path = OUTPUT_DIR / f"{name}.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✅ {path.name} — {len(rows)} rows")

print("\n✅ All data generated successfully in /data folder!")
print("Next step: Run load_to_bigquery.py to upload to BigQuery.")
