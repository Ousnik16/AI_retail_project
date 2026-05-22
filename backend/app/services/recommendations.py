from collections import Counter
from typing import Dict, List

from app.db.database import get_collection
from pymongo.errors import PyMongoError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

OFFER_RULES = {
    "laptop": ["Wireless Mouse", "Mechanical Keyboard", "Laptop Bag"],
    "monitor": ["Mechanical Keyboard", "Wireless Mouse", "HDMI Cable"],
    "gaming": ["Gaming Monitor", "Mechanical Keyboard", "Wireless Mouse"],
}

FALLBACK_RECOMMENDATIONS = []

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
                        "price": doc.get("price", 0.0),
                        "category": doc.get("category", ""),
                        "brand": doc.get("brand", ""),
                        "tags": doc.get("tags", []),
                        "tags_text": " ".join(doc.get("tags", [])),
                    }
                )
        except (PyMongoError, RuntimeError):
            products = []
        # If products collection is empty, derive product entries from historical transactions
        if not products:
            try:
                transactions = get_collection("transactions")
                pipeline = [
                    {"$unwind": "$products"},
                    {"$group": {"_id": "$products.product_id", "name": {"$first": "$products.name"}, "category": {"$first": "$products.category"}, "price": {"$first": "$products.unit_price"}}},
                ]
                derived = await transactions.aggregate(pipeline).to_list(length=1000)
                for item in derived:
                    products.append(
                        {
                            "id": item["_id"],
                            "name": item.get("name", item["_id"]),
                            "price": float(item.get("price") or 0.0),
                            "category": item.get("category", ""),
                            "brand": "",
                            "tags": [],
                            "tags_text": "",
                        }
                    )
            except (PyMongoError, RuntimeError):
                products = []
        return products

    @staticmethod
    async def _load_product_popularity() -> Dict[str, int]:
        popularity: Dict[str, int] = {}
        try:
            transactions = get_collection("transactions")
            pipeline = [
                {"$unwind": "$products"},
                {"$group": {"_id": "$products.product_id", "count": {"$sum": "$products.quantity"}}},
            ]
            popular = await transactions.aggregate(pipeline).to_list(length=1000)
            for item in popular:
                popularity[item["_id"]] = int(item.get("count", 0))
        except (PyMongoError, RuntimeError):
            pass
        return popularity

    @staticmethod
    def _build_user_profile(purchased_items: List[Dict]) -> Dict[str, object]:
        categories = Counter()
        brands = Counter()
        tags = Counter()

        for item in purchased_items:
            quantity = item.get("quantity", 1) or 1
            categories[item.get("category", "").lower()] += quantity
            brands[item.get("brand", "").lower()] += quantity
            for tag in item.get("tags", []):
                tags[str(tag).lower()] += quantity

        top_categories = [category for category, _ in categories.most_common(3) if category]
        top_brands = [brand for brand, _ in brands.most_common(3) if brand]
        top_tags = {tag for tag, _ in tags.most_common(10)} if tags else set()
        favorite_category = top_categories[0] if top_categories else None

        return {
            "top_categories": top_categories,
            "top_brands": top_brands,
            "top_tags": top_tags,
            "favorite_category": favorite_category,
        }

    @staticmethod
    def _score_product(product: Dict, profile: Dict[str, object], popularity: Dict[str, int]) -> int:
        score = 0
        product_category = product.get("category", "").lower()
        product_brand = product.get("brand", "").lower()
        product_tags = {str(tag).lower() for tag in product.get("tags", [])}

        if profile["favorite_category"] and product_category == profile["favorite_category"]:
            score += 40
        if product_brand in profile["top_brands"]:
            score += 25

        tag_overlap = len(product_tags.intersection(profile["top_tags"]))
        score += tag_overlap * 10
        score += popularity.get(product["id"], 0) * 2

        return score

    @staticmethod
    def _recommendation_reason(product: Dict, profile: Dict[str, object]) -> str:
        parts = []
        if profile["favorite_category"] and product.get("category", "").lower() == profile["favorite_category"]:
            parts.append(f"Based on your interest in {profile['favorite_category'].title()} products")
        if product.get("brand", "").lower() in profile["top_brands"]:
            parts.append(f"From your preferred brand {product['brand']}")
        if set(str(tag).lower() for tag in product.get("tags", [])).intersection(profile["top_tags"]):
            parts.append("Shares tags with products you purchase frequently")
        return parts[0] if parts else "A great match for your shopping behavior"

    @staticmethod
    def _bundle_offers_for_user(purchased_ids: set[str], products_by_id: Dict[str, Dict]) -> List[str]:
        offers = []
        for product_id in purchased_ids:
            key = str(product_id).lower()
            for trigger, bundle in OFFER_RULES.items():
                if trigger in key:
                    for item in bundle:
                        if item not in purchased_ids:
                            offers.append(item)
        return sorted(set(offers))[:5]

    @staticmethod
    async def user_recommendations(user_id: str):
        try:
            transactions = get_collection("transactions")
            user_cursor = transactions.find({"user_id": user_id}).sort("purchased_at", -1)
            products = await RecommendationService._load_products()
            products_by_id = {product["id"]: product for product in products}

            purchased_items = []
            recent_purchases = []
            order_count = 0

            async for tx in user_cursor:
                order_count += 1
                for item in tx.get("products", []):
                    product_id = item.get("product_id")
                    reference = products_by_id.get(product_id, {})
                    enriched = {
                        **item,
                        "category": item.get("category") or reference.get("category", ""),
                        "brand": reference.get("brand", ""),
                        "tags": reference.get("tags", []),
                        "name": item.get("name") or reference.get("name", product_id),
                    }
                    purchased_items.append(enriched)
                    recent_purchases.append(
                        {
                            "product_id": product_id,
                            "name": enriched["name"],
                            "quantity": enriched.get("quantity", 1),
                            "purchased_at": tx.get("purchased_at"),
                        }
                    )

            if purchased_items:
                profile = RecommendationService._build_user_profile(purchased_items)
                popularity = await RecommendationService._load_product_popularity()
                purchased_ids = {item.get("product_id") for item in purchased_items if item.get("product_id")}
                candidates = [product for product in products if product["id"] not in purchased_ids]

                scored_recommendations = []
                for candidate in candidates:
                    score = RecommendationService._score_product(candidate, profile, popularity)
                    if score <= 0:
                        continue
                    scored_recommendations.append(
                        {
                            "product_id": candidate["id"],
                            "name": candidate["name"],
                            "category": candidate.get("category", ""),
                            "brand": candidate.get("brand", ""),
                            "price": candidate.get("price", 0.0),
                            "reason": RecommendationService._recommendation_reason(candidate, profile),
                            "score": score,
                        }
                    )

                scored_recommendations.sort(key=lambda item: item["score"], reverse=True)
                recommendations = scored_recommendations[:5]

                if len(recommendations) < 5:
                    additional = sorted(
                        [
                            {
                                "product_id": product["id"],
                                "name": product["name"],
                                "category": product.get("category", ""),
                                "reason": "Popular product you have not purchased yet",
                                "price": product.get("price", 0.0),
                                "score": popularity.get(product["id"], 0),
                            }
                            for product in products
                            if product["id"] not in purchased_ids and product["id"] not in {item["product_id"] for item in recommendations}
                        ],
                        key=lambda x: x["score"],
                        reverse=True,
                    )
                    recommendations.extend(additional[: max(0, 5 - len(recommendations))])

                if not recommendations:
                    recommendations = [
                        {
                            "product_id": product["id"],
                            "name": product["name"],
                            "category": product.get("category", ""),
                            "price": product.get("price", 0.0),
                            "reason": "Popular item among customers",
                        }
                        for product in products[:5]
                    ]

                offers = RecommendationService._bundle_offers_for_user(purchased_ids, products_by_id)
                if not offers and profile["favorite_category"]:
                    offers = [f"Save on more {profile['favorite_category'].title()} items"]

                recent_purchases = sorted(recent_purchases, key=lambda item: item["purchased_at"], reverse=True)[:5]
                return {
                    "user_id": user_id,
                    "recommendations": recommendations,
                    "personalized_offers": offers,
                    "user_profile": {
                        "orders": order_count,
                        "total_spent": sum(item.get("total", 0) for item in purchased_items),
                        "top_categories": profile["top_categories"],
                        "top_brands": profile["top_brands"],
                        "favorite_category": profile["favorite_category"],
                    },
                    "recent_purchases": recent_purchases,
                }
        except (PyMongoError, RuntimeError):
            pass

        return {
            "user_id": user_id,
            "recommendations": [],
            "personalized_offers": [],
            "user_profile": {"orders": 0, "total_spent": 0.0, "top_categories": [], "top_brands": [], "favorite_category": None},
            "recent_purchases": [],
        }
