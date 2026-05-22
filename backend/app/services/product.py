from app.db.database import get_collection
from app.schemas.product import ProductCreate, ProductUpdate
from pymongo.errors import PyMongoError
from bson import ObjectId

DEMO_PRODUCTS = [
    {
        "id": "laptop-pro-15",
        "sku": "LAP-001",
        "name": "Laptop Pro 15",
        "category": "Computers",
        "price": 1299.0,
        "brand": "Apex",
        "inventory_quantity": 24,
        "stock_alert_threshold": 10,
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
        "stock_alert_threshold": 20,
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
        "stock_alert_threshold": 15,
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
        "stock_alert_threshold": 12,
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
        "stock_alert_threshold": 10,
        "tags": ["monitor", "gaming", "display"],
    },
]

class ProductService:
    @staticmethod
    def _product_query(product_id: str):
        query = {"$or": [{"sku": product_id}, {"id": product_id}]}
        try:
            query["$or"].append({"_id": ObjectId(product_id)})
        except Exception:
            pass
        return query

    @staticmethod
    def _serialize_product(product: dict):
        return {
            "id": str(product.get("_id") or product.get("id") or product.get("sku")),
            **{k: v for k, v in product.items() if k != "_id"},
            "stock_alert_threshold": product.get("stock_alert_threshold", 10),
        }

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
                products.append(ProductService._serialize_product(product))
            return products or DEMO_PRODUCTS
        except (PyMongoError, RuntimeError):
            return DEMO_PRODUCTS

    @staticmethod
    async def update_product(product_id: str, payload: ProductUpdate):
        collection = get_collection("products")
        product = await collection.find_one(ProductService._product_query(product_id))
        if not product:
            return None

        updates = payload.dict(exclude_unset=True)
        if not updates:
            return ProductService._serialize_product(product)

        await collection.update_one({"_id": product["_id"]}, {"$set": updates})
        updated = await collection.find_one({"_id": product["_id"]})
        return ProductService._serialize_product(updated)

    @staticmethod
    async def delete_product(product_id: str):
        collection = get_collection("products")
        product = await collection.find_one(ProductService._product_query(product_id))
        if not product:
            return None

        await collection.delete_one({"_id": product["_id"]})
        return {"deleted": True, "id": str(product["_id"])}
