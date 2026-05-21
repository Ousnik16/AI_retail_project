from app.db.database import get_collection
from app.schemas.product import ProductCreate
from pymongo.errors import PyMongoError

DEMO_PRODUCTS = [
    {
        "id": "laptop-pro-15",
        "sku": "LAP-001",
        "name": "Laptop Pro 15",
        "category": "Computers",
        "price": 1299.0,
        "brand": "Apex",
        "inventory_quantity": 24,
        "tags": ["laptop", "tech", "productivity"],
    },
    {
        "id": "wireless-mouse",
        "sku": "ACC-101",
        "name": "Wireless Mouse",
        "category": "Accessories",
        "price": 39.0,
        "brand": "Apex",
        "inventory_quantity": 120,
        "tags": ["mouse", "laptop", "accessory"],
    },
    {
        "id": "mechanical-keyboard",
        "sku": "ACC-102",
        "name": "Mechanical Keyboard",
        "category": "Accessories",
        "price": 89.0,
        "brand": "Keylab",
        "inventory_quantity": 76,
        "tags": ["keyboard", "gaming", "accessory"],
    },
    {
        "id": "laptop-bag",
        "sku": "BAG-201",
        "name": "Laptop Bag",
        "category": "Bags",
        "price": 59.0,
        "brand": "CarryCo",
        "inventory_quantity": 44,
        "tags": ["bag", "laptop", "travel"],
    },
    {
        "id": "gaming-monitor",
        "sku": "MON-301",
        "name": "Gaming Monitor",
        "category": "Displays",
        "price": 329.0,
        "brand": "PixelForge",
        "inventory_quantity": 31,
        "tags": ["monitor", "gaming", "display"],
    },
]

class ProductService:
    @staticmethod
    async def create_product(payload: ProductCreate):
        collection = get_collection("products")
        result = await collection.insert_one(payload.dict())
        return {"id": str(result.inserted_id), **payload.dict()}

    @staticmethod
    async def list_products():
        try:
            collection = get_collection("products")
            cursor = collection.find({})
            products = []
            async for product in cursor:
                products.append({"id": str(product["_id"]), **{k: v for k, v in product.items() if k != "_id"}})
            return products or DEMO_PRODUCTS
        except (PyMongoError, RuntimeError):
            return DEMO_PRODUCTS
