import csv
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from passlib.context import CryptContext
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend"))

from app.core.config import settings

DATA_FILE = ROOT / "data" / "synthetic_retail_intelligence.csv"

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

products = [
    {"sku": "laptop-pro-15", "name": "Laptop Pro 15", "category": "Computers", "price": 1299.00, "brand": "Apex", "inventory_quantity": 32, "tags": ["laptop", "productivity", "premium"]},
    {"sku": "wireless-mouse", "name": "Wireless Mouse", "category": "Accessories", "price": 39.00, "brand": "Apex", "inventory_quantity": 180, "tags": ["mouse", "wireless", "laptop"]},
    {"sku": "mechanical-keyboard", "name": "Mechanical Keyboard", "category": "Accessories", "price": 89.00, "brand": "KeyLab", "inventory_quantity": 96, "tags": ["keyboard", "gaming", "productivity"]},
    {"sku": "laptop-bag", "name": "Laptop Bag", "category": "Bags", "price": 59.00, "brand": "CarryCo", "inventory_quantity": 74, "tags": ["bag", "laptop", "travel"]},
    {"sku": "gaming-monitor", "name": "Gaming Monitor", "category": "Displays", "price": 329.00, "brand": "PixelForge", "inventory_quantity": 46, "tags": ["monitor", "gaming", "display"]},
    {"sku": "noise-cancelling-headphones", "name": "Noise Cancelling Headphones", "category": "Audio", "price": 199.00, "brand": "SoundCore", "inventory_quantity": 88, "tags": ["headphones", "audio", "travel"]},
    {"sku": "usb-c-hub", "name": "USB-C Hub", "category": "Accessories", "price": 49.00, "brand": "PortWorks", "inventory_quantity": 140, "tags": ["hub", "usb-c", "laptop"]},
    {"sku": "smartwatch-fit", "name": "Smartwatch Fit", "category": "Wearables", "price": 179.00, "brand": "Pulse", "inventory_quantity": 70, "tags": ["watch", "fitness", "mobile"]},
    {"sku": "4k-webcam", "name": "4K Webcam", "category": "Cameras", "price": 119.00, "brand": "Streamio", "inventory_quantity": 62, "tags": ["webcam", "remote-work", "video"]},
    {"sku": "tablet-air", "name": "Tablet Air", "category": "Tablets", "price": 549.00, "brand": "Apex", "inventory_quantity": 38, "tags": ["tablet", "mobile", "creative"]},
]

users = [
    {"email": "admin@retail.ai", "name": "Retail Admin", "password_hash": pwd_context.hash("Admin123"), "roles": ["admin"]},
    {"email": "customer@retail.ai", "name": "Demo Customer", "password_hash": pwd_context.hash("Customer123"), "roles": ["customer"]},
    {"email": "alice@example.com", "name": "Alice Morgan", "password_hash": pwd_context.hash("Customer123"), "roles": ["customer"]},
    {"email": "bob@example.com", "name": "Bob Singh", "password_hash": pwd_context.hash("Customer123"), "roles": ["customer"]},
    {"email": "mira@example.com", "name": "Mira Chen", "password_hash": pwd_context.hash("Customer123"), "roles": ["customer"]},
]

reviews = [
    {"user_id": "customer@retail.ai", "product_id": "laptop-pro-15", "rating": 5, "title": "Great work laptop", "review_text": "Fast, light, and perfect for analytics work."},
    {"user_id": "alice@example.com", "product_id": "gaming-monitor", "rating": 5, "title": "Excellent display", "review_text": "The refresh rate is smooth and color quality is excellent."},
    {"user_id": "bob@example.com", "product_id": "wireless-mouse", "rating": 4, "title": "Reliable accessory", "review_text": "Comfortable and pairs well with my laptop."},
    {"user_id": "mira@example.com", "product_id": "noise-cancelling-headphones", "rating": 3, "title": "Good sound", "review_text": "Sound is strong, but the ear cups feel warm after long sessions."},
]

bundle_rules = {
    "laptop-pro-15": ["wireless-mouse", "laptop-bag", "usb-c-hub"],
    "gaming-monitor": ["mechanical-keyboard", "wireless-mouse"],
    "tablet-air": ["noise-cancelling-headphones", "usb-c-hub"],
}


def build_transactions(days: int = 90) -> list[dict]:
    random.seed(42)
    customers = [user["email"] for user in users if "customer" in user["roles"]]
    transactions = []
    for index in range(180):
        purchased_at = datetime.utcnow() - timedelta(days=random.randint(0, days), hours=random.randint(0, 23))
        anchor = random.choice(products)
        item_skus = [anchor["sku"]]
        if anchor["sku"] in bundle_rules and random.random() < 0.72:
            item_skus.extend(random.sample(bundle_rules[anchor["sku"]], k=random.randint(1, len(bundle_rules[anchor["sku"]]))))
        elif random.random() < 0.35:
            item_skus.append(random.choice(products)["sku"])

        items = []
        for sku in sorted(set(item_skus)):
            product = next(item for item in products if item["sku"] == sku)
            quantity = random.randint(1, 3 if product["price"] < 100 else 1)
            items.append(
                {
                    "product_id": product["sku"],
                    "name": product["name"],
                    "category": product["category"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "total": round(quantity * product["price"], 2),
                }
            )

        transactions.append(
            {
                "user_id": random.choice(customers),
                "products": items,
                "total_amount": round(sum(item["total"] for item in items), 2),
                "purchased_at": purchased_at,
                "channel": random.choice(["store", "online", "mobile"]),
                "status": "completed",
                "season": "holiday" if purchased_at.month in {11, 12} else "back_to_school" if purchased_at.month in {7, 8, 9} else "regular",
            }
        )
    return transactions


def write_csv(transactions: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "transaction_id",
                "user_id",
                "purchased_at",
                "channel",
                "season",
                "product_id",
                "product_name",
                "category",
                "quantity",
                "unit_price",
                "line_total",
                "basket_size",
                "transaction_total",
            ],
        )
        writer.writeheader()
        for tx_index, tx in enumerate(transactions, start=1):
            for item in tx["products"]:
                writer.writerow(
                    {
                        "transaction_id": f"TX-{tx_index:04d}",
                        "user_id": tx["user_id"],
                        "purchased_at": tx["purchased_at"].isoformat(),
                        "channel": tx["channel"],
                        "season": tx["season"],
                        "product_id": item["product_id"],
                        "product_name": item["name"],
                        "category": item["category"],
                        "quantity": item["quantity"],
                        "unit_price": item["unit_price"],
                        "line_total": item["total"],
                        "basket_size": len(tx["products"]),
                        "transaction_total": tx["total_amount"],
                    }
                )


if __name__ == "__main__":
    transactions = build_transactions()
    browsing_events = [
        {
            "user_id": random.choice([user["email"] for user in users if "customer" in user["roles"]]),
            "product_id": random.choice(products)["sku"],
            "event_type": random.choice(["view", "compare", "add_to_wishlist"]),
            "session_id": f"session-{index:03d}",
            "created_at": datetime.utcnow() - timedelta(hours=index),
        }
        for index in range(60)
    ]

    db.products.delete_many({})
    db.users.delete_many({})
    db.reviews.delete_many({})
    db.transactions.delete_many({})
    db.browsing_history.delete_many({})

    db.products.insert_many(products)
    db.users.insert_many(users)
    db.reviews.insert_many(reviews)
    db.transactions.insert_many(transactions)
    db.browsing_history.insert_many(browsing_events)
    write_csv(transactions)

    print(f"Inserted {len(products)} products, {len(users)} users, {len(transactions)} transactions, and {len(reviews)} reviews.")
    print(f"Wrote analytics CSV to {DATA_FILE}")
