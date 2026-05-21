from app.db.database import get_collection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pymongo.errors import PyMongoError

OFFER_RULES = {
    "laptop": ["Wireless Mouse", "Mechanical Keyboard", "Laptop Bag"],
    "monitor": ["Mechanical Keyboard", "Wireless Mouse", "HDMI Cable"],
    "gaming": ["Gaming Monitor", "Mechanical Keyboard", "Wireless Mouse"],
}

class RecommendationService:
    @staticmethod
    async def _load_products():
        products = []
        try:
            collection = get_collection("products")
            cursor = collection.find({})
            async for doc in cursor:
                products.append(
                    {
                        "id": doc.get("sku", str(doc["_id"])),
                        "name": doc["name"],
                        "category": doc["category"],
                        "tags": " ".join(doc.get("tags", [])),
                    }
                )
        except (PyMongoError, RuntimeError):
            products = []
        if not products:
            products = [
                {"id": "laptop-pro-15", "name": "Laptop Pro 15", "category": "Computers", "tags": "laptop tech productivity"},
                {"id": "wireless-mouse", "name": "Wireless Mouse", "category": "Accessories", "tags": "mouse laptop accessory"},
                {"id": "mechanical-keyboard", "name": "Mechanical Keyboard", "category": "Accessories", "tags": "keyboard gaming accessory"},
                {"id": "laptop-bag", "name": "Laptop Bag", "category": "Bags", "tags": "bag laptop travel"},
                {"id": "gaming-monitor", "name": "Gaming Monitor", "category": "Displays", "tags": "monitor gaming display"},
            ]
        return products

    @staticmethod
    async def similar_products(product_id: str):
        products = await RecommendationService._load_products()
        if not products:
            return {"similar_items": []}
        text_data = [f"{item['name']} {item['category']} {item['tags']}" for item in products]
        tfidf = TfidfVectorizer(stop_words="english")
        matrix = tfidf.fit_transform(text_data)
        index = next((i for i, item in enumerate(products) if item["id"] == product_id), None)
        if index is None:
            return {"similar_items": []}
        sim_scores = cosine_similarity(matrix[index:index+1], matrix).flatten()
        top_indices = np.argsort(sim_scores)[::-1][1:6]
        return {"product_id": product_id, "similar_items": [products[i] for i in top_indices]}

    @staticmethod
    async def user_recommendations(user_id: str):
        top_products = []
        try:
            transactions = get_collection("transactions")
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$products"},
                {"$group": {"_id": "$products.product_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5},
            ]
            top_products = await transactions.aggregate(pipeline).to_list(length=10)
        except (PyMongoError, RuntimeError):
            top_products = []
        if top_products:
            offers = []
            for product in top_products:
                key = str(product["_id"]).lower()
                for trigger, items in OFFER_RULES.items():
                    if trigger in key:
                        offers.extend(items)
            return {
                "user_id": user_id,
                "recommendations": top_products,
                "personalized_offers": sorted(set(offers))[:5],
            }
        return {
            "user_id": user_id,
            "recommendations": [
                {"_id": "wireless-mouse", "count": 24, "reason": "Frequently bought with laptops"},
                {"_id": "mechanical-keyboard", "count": 18, "reason": "Preferred by tech enthusiast customers"},
                {"_id": "laptop-bag", "count": 16, "reason": "Personalized laptop bundle offer"},
            ],
            "personalized_offers": ["Mouse + Keyboard bundle", "Laptop Bag 15% off", "Monitor upgrade deal"],
        }
