from collections import Counter
from typing import Dict, List

from app.db.database import get_collection
from pymongo.errors import PyMongoError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.ml.recommender import ContentRecommender

OFFER_RULES = {
    "laptop": ["Wireless Mouse", "Mechanical Keyboard", "Laptop Bag"],
    "monitor": ["Mechanical Keyboard", "Wireless Mouse", "HDMI Cable"],
    "gaming": ["Gaming Monitor", "Mechanical Keyboard", "Wireless Mouse"],
}

FALLBACK_RECOMMENDATIONS = []

class RecommendationService:
    CATEGORY_FAMILIES = {
        "clothing": {
            "apparel",
            "clothes",
            "clothing",
            "dress",
            "dresses",
            "fashion",
            "footwear",
            "jeans",
            "pants",
            "shirt",
            "shirts",
            "shoes",
            "t-shirt",
            "t-shirts",
            "tshirt",
            "tshirts",
        },
        "electronics": {
            "audio",
            "cameras",
            "computers",
            "displays",
            "electronics",
            "gaming",
            "laptops",
            "mobiles",
            "phones",
            "tablets",
            "tech",
            "wearables",
        },
        "accessories": {
            "accessory",
            "accessories",
            "cable",
            "charger",
            "case",
            "bag",
            "cover",
            "hdmi",
            "adapter",
            "mouse",
            "keyboard",
            "bag",
            "headphones",
            "speaker",
        },
    }

    @staticmethod
    def _normalize_category(category: str | None) -> str:
        return (category or "").strip().lower()

    @staticmethod
    def _category_family(category: str | None) -> str:
        normalized = RecommendationService._normalize_category(category)
        for family, aliases in RecommendationService.CATEGORY_FAMILIES.items():
            if normalized in aliases:
                return family
            if any(alias in normalized for alias in aliases):
                return family
        return normalized

    @staticmethod
    def _matches_profile_category(product: Dict, profile: Dict[str, object]) -> bool:
        top_categories = set(profile.get("top_categories") or [])
        if not top_categories:
            return True
        product_category = RecommendationService._normalize_category(product.get("category"))
        product_family = RecommendationService._category_family(product_category)
        profile_families = {
            RecommendationService._category_family(category)
            for category in top_categories
        }
        return product_category in top_categories or product_family in profile_families

    @staticmethod
    def _normalize_tags(tags) -> set[str]:
        return {str(tag).lower() for tag in tags or []}

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
        # If products collection is empty, derive product entries from ALL historical transactions
        # to build a comprehensive catalog of products available for recommendation
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
            categories[RecommendationService._normalize_category(item.get("category"))] += quantity
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
        if not RecommendationService._matches_profile_category(product, profile):
            return 0

        score = 0
        product_category = RecommendationService._normalize_category(product.get("category"))
        product_brand = product.get("brand", "").lower()
        product_tags = RecommendationService._normalize_tags(product.get("tags"))
        product_family = RecommendationService._category_family(product_category)

        if profile["favorite_category"] and product_category == profile["favorite_category"]:
            score += 40
        # boost items in the same category family as user's top categories
        profile_families = {RecommendationService._category_family(cat) for cat in profile.get("top_categories")}
        if product_family in profile_families:
            score += 20
        if product_brand in profile["top_brands"]:
            score += 25

        tag_overlap = len(product_tags.intersection(profile["top_tags"]))
        score += tag_overlap * 10
        score += popularity.get(product["id"], 0) * 2

        return score

    @staticmethod
    def _recommendation_reason(product: Dict, profile: Dict[str, object]) -> str:
        parts = []
        if profile["favorite_category"] and RecommendationService._normalize_category(product.get("category")) == profile["favorite_category"]:
            parts.append(f"Based on your interest in {profile['favorite_category'].title()} products")
        if product.get("brand", "").lower() in profile["top_brands"]:
            parts.append(f"From your preferred brand {product['brand']}")
        if RecommendationService._normalize_tags(product.get("tags")).intersection(profile["top_tags"]):
            parts.append("Shares tags with products you purchase frequently")
        return parts[0] if parts else "A great match for your shopping behavior"

    @staticmethod
    def _bundle_offers_for_user(purchased_ids: set[str], products_by_id: Dict[str, Dict]) -> List[str]:
        offers = []
        for product_id in purchased_ids:
            prod = products_by_id.get(product_id, {})
            # create a searchable string from id, name, category and tags
            key_parts = [str(product_id), prod.get("name", ""), prod.get("category", "")]
            key_parts.extend(prod.get("tags", []))
            key = " ".join([str(p).lower() for p in key_parts if p])
            for trigger, bundle in OFFER_RULES.items():
                if trigger in key:
                    for item in bundle:
                        if item not in purchased_ids:
                            offers.append(item)
        return sorted(set(offers))[:5]

    @staticmethod
    async def user_recommendations(user_id: str, debug: bool = False):
        try:
            transactions = get_collection("transactions")
            user_cursor = transactions.find({"user_id": user_id}).sort("purchased_at", -1)
            products = await RecommendationService._load_products()
            products_by_id = {product["id"]: product for product in products}

            # If products collection is empty or does not contain many items,
            # derive additional product metadata from historical transactions so
            # there are candidates to recommend.
            if not products or len(products) < 5:
                try:
                    pipeline = [
                        {"$unwind": "$products"},
                        {"$group": {"_id": "$products.product_id", "name": {"$first": "$products.name"}, "category": {"$first": "$products.category"}, "price": {"$first": "$products.unit_price"}}},
                    ]
                    derived = await transactions.aggregate(pipeline).to_list(length=1000)
                    for item in derived:
                        pid = item["_id"]
                        if pid not in products_by_id:
                            entry = {
                                "id": pid,
                                "name": item.get("name", pid),
                                "price": float(item.get("price") or 0.0),
                                "category": item.get("category", ""),
                                "brand": "",
                                "tags": [],
                                "tags_text": "",
                            }
                            products.append(entry)
                            products_by_id[pid] = entry
                except Exception:
                    pass

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

                # If there are no explicit candidates, populate from ALL products (not just from user's purchases)
                # Ensures we have items to recommend that user hasn't bought yet.
                if not candidates:
                    all_product_ids = {p.get("id") for p in products}
                    # try to fetch from the aggregated catalog of all products across all transactions
                    try:
                        popular = await transactions.aggregate([
                            {"$unwind": "$products"},
                            {"$group": {"_id": "$products.product_id", "name": {"$first": "$products.name"}, "category": {"$first": "$products.category"}, "count": {"$sum": "$products.quantity"}}},
                            {"$sort": {"count": -1}},
                        ]).to_list(length=100)
                        for item in popular:
                            pid = item.get("_id")
                            if pid and pid not in purchased_ids and pid not in all_product_ids:
                                candidates.append({
                                    "id": pid,
                                    "name": item.get("name", str(pid)),
                                    "category": item.get("category", ""),
                                    "brand": "",
                                    "price": 0.0,
                                    "tags": [],
                                    "tags_text": ""
                                })
                    except Exception:
                        pass
                    # If still no candidates, add the popular items directly
                    if not candidates:
                        try:
                            popular = await transactions.aggregate([
                                {"$unwind": "$products"},
                                {"$group": {"_id": "$products.product_id", "name": {"$first": "$products.name"}, "category": {"$first": "$products.category"}, "count": {"$sum": "$products.quantity"}}},
                                {"$sort": {"count": -1}},
                            ]).to_list(length=100)
                            for item in popular[:20]:
                                pid = item.get("_id")
                                if pid and pid not in purchased_ids:
                                    candidates.append({
                                        "id": pid,
                                        "name": item.get("name", str(pid)),
                                        "category": item.get("category", ""),
                                        "brand": "",
                                        "price": 0.0,
                                        "tags": [],
                                        "tags_text": ""
                                    })
                        except Exception:
                            pass

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
                            if product["id"] not in purchased_ids
                            and product["id"] not in {item["product_id"] for item in recommendations}
                            and RecommendationService._matches_profile_category(product, profile)
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
                        for product in products
                        if product["id"] not in purchased_ids
                        and RecommendationService._matches_profile_category(product, profile)
                    ]
                    recommendations = recommendations[:5]

                offers = RecommendationService._bundle_offers_for_user(purchased_ids, products_by_id)
                if not offers and profile["favorite_category"]:
                    offers = [f"Save on more {profile['favorite_category'].title()} items"]

                recent_purchases = sorted(recent_purchases, key=lambda item: item["purchased_at"], reverse=True)[:5]
                result = {
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
                if debug:
                    result["diagnostics"] = {
                        "products_in_catalog": len(products),
                        "products_by_id_count": len(products_by_id),
                        "purchased_items_count": len(purchased_items),
                        "candidate_count": len(candidates),
                        "scored_recommendations_count": len(scored_recommendations),
                        "final_recommendations_count": len(recommendations),
                    }
                return result
        except (PyMongoError, RuntimeError):
            pass

        result = {
            "user_id": user_id,
            "recommendations": [],
            "personalized_offers": [],
            "user_profile": {"orders": 0, "total_spent": 0.0, "top_categories": [], "top_brands": [], "favorite_category": None},
            "recent_purchases": [],
        }
        if debug:
            # provide some basic diagnostics when nothing was found
            result["diagnostics"] = {
                "products_in_catalog": len(products) if 'products' in locals() else 0,
                "purchased_items_count": 0,
                "candidate_count": 0,
                "final_recommendations_count": 0,
            }
        return result

    @staticmethod
    async def similar_products(product_id: str, top_n: int = 5):
        products = await RecommendationService._load_products()
        if not products:
            return {"product_id": product_id, "similar_items": []}
        recommender = ContentRecommender(products)
        similar = recommender.recommend_similar(product_id, top_n=top_n)
        similar_items = [
            {
                "product_id": item.get("id"),
                "name": item.get("name"),
                "category": item.get("category", ""),
                "brand": item.get("brand", ""),
                "price": item.get("price", 0.0),
            }
            for item in similar
        ]
        return {"product_id": product_id, "similar_items": similar_items}
