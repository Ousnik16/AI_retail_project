from app.db.database import get_collection
from datetime import datetime
from collections import Counter, defaultdict
from pymongo.errors import PyMongoError

DEMO_CUSTOMERS = [
    {
        "user_id": "demo_user_id",
        "total_spent": 1777,
        "orders": 3,
        "purchase_frequency": 3,
        "preferred_categories": ["Computers", "Accessories", "Displays"],
        "seasonal_behaviour": "Back-to-school and holiday tech spikes",
        "persona": "Tech Enthusiast",
        "buying_patterns": ["Laptop", "Gaming Accessories", "Monitor"],
    }
]

class AnalyticsService:
    @staticmethod
    async def customer_segmentation():
        try:
            collection = get_collection("transactions")
            pipeline = [
                {"$group": {"_id": "$user_id", "total_spent": {"$sum": "$total_amount"}, "orders": {"$sum": 1}}},
                {"$project": {"user_id": "$_id", "total_spent": 1, "orders": 1, "persona": {"$switch": {
                    "branches": [
                        {"case": {"$gte": ["$total_spent", 1000]}, "then": "Frequent Buyer"},
                        {"case": {"$gte": ["$orders", 5]}, "then": "Seasonal Customer"},
                    ],
                    "default": "Budget Shopper"
                }}}},
            ]
            cursor = collection.aggregate(pipeline)
            results = []
            async for row in cursor:
                row.pop("_id", None)
                results.append(row)
            return {"customer_segments": results or DEMO_CUSTOMERS}
        except (PyMongoError, RuntimeError):
            return {"customer_segments": DEMO_CUSTOMERS}

    @staticmethod
    async def sales_summary():
        try:
            collection = get_collection("transactions")
            pipeline = [
                {"$group": {"_id": None, "total_sales": {"$sum": "$total_amount"}, "order_count": {"$sum": 1}}},
                {"$project": {"_id": 0, "total_sales": 1, "order_count": 1}},
            ]
            summary = await collection.aggregate(pipeline).to_list(length=1)
            return summary[0] if summary else {"total_sales": 18432, "order_count": 86}
        except (PyMongoError, RuntimeError):
            return {"total_sales": 18432, "order_count": 86}

    @staticmethod
    async def sales_by_day(days: int = 30, user_id: str | None = None):
        try:
            collection = get_collection("transactions")
            match = {"purchased_at": {"$exists": True}}
            if user_id:
                match["user_id"] = user_id
            pipeline = [
                {"$match": match},
                {"$project": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$purchased_at"}}, "total_amount": 1}},
                {"$group": {"_id": "$date", "total_sales": {"$sum": "$total_amount"}, "orders": {"$sum": 1}}},
                {"$sort": {"_id": 1}},
            ]
            rows = await collection.aggregate(pipeline).to_list(length=1000)
            # keep only the last `days` entries
            data = [{"date": row["_id"], "total_sales": row.get("total_sales", 0), "orders": row.get("orders", 0)} for row in rows]
            return data[-days:]
        except (PyMongoError, RuntimeError):
            # fallback sample series
            return [
                {"date": "2024-08-01", "total_sales": 4000, "orders": 12},
                {"date": "2024-08-02", "total_sales": 3200, "orders": 9},
                {"date": "2024-08-03", "total_sales": 4500, "orders": 14},
            ]

    @staticmethod
    async def spending_by_category(user_id: str | None = None):
        try:
            collection = get_collection("transactions")
            pipeline = []
            if user_id:
                pipeline.append({"$match": {"user_id": user_id}})
            pipeline.extend([
                {"$unwind": "$products"},
                {"$group": {"_id": "$products.category", "total_spent": {"$sum": "$products.total"}}},
                {"$sort": {"total_spent": -1}},
            ])
            rows = await collection.aggregate(pipeline).to_list(length=1000)
            return [{"category": (row["_id"] or "Uncategorized"), "total_spent": row.get("total_spent", 0)} for row in rows]
        except (PyMongoError, RuntimeError):
            return [{"category": "Computers", "total_spent": 12000}, {"category": "Accessories", "total_spent": 4200}, {"category": "Displays", "total_spent": 3200}]

    @staticmethod
    async def top_selling_products():
        try:
            collection = get_collection("transactions")
            pipeline = [
                {"$unwind": "$products"},
                {"$group": {
                    "_id": "$products.product_id",
                    "name": {"$first": "$products.name"},
                    "category": {"$first": "$products.category"},
                    "units": {"$sum": "$products.quantity"},
                    "revenue": {"$sum": "$products.total"},
                }},
                {"$sort": {"units": -1}},
                {"$limit": 5},
            ]
            rows = await collection.aggregate(pipeline).to_list(length=5)
            if rows:
                return [{"product_id": row["_id"], **{k: v for k, v in row.items() if k != "_id"}} for row in rows]
        except (PyMongoError, RuntimeError):
            pass
        return [
            {"product_id": "laptop-pro-15", "name": "Laptop Pro 15", "category": "Computers", "units": 12, "revenue": 15588},
            {"product_id": "wireless-mouse", "name": "Wireless Mouse", "category": "Accessories", "units": 31, "revenue": 1209},
            {"product_id": "mechanical-keyboard", "name": "Mechanical Keyboard", "category": "Accessories", "units": 18, "revenue": 1602},
        ]

    @staticmethod
    async def basket_analysis():
        combinations = []
        try:
            collection = get_collection("transactions")
            baskets = []
            async for tx in collection.find({}):
                product_ids = sorted({item["product_id"] for item in tx.get("products", [])})
                if len(product_ids) > 1:
                    baskets.append(product_ids)

            pairs = Counter()
            for basket in baskets:
                for index, left in enumerate(basket):
                    for right in basket[index + 1:]:
                        pairs[(left, right)] += 1

            combinations = [
                {"products": list(pair), "support_count": count}
                for pair, count in pairs.most_common(8)
            ]
        except (PyMongoError, RuntimeError):
            combinations = []
        if not combinations:
            combinations = [
                {"products": ["Laptop Pro 15", "Wireless Mouse"], "support_count": 24},
                {"products": ["Laptop Pro 15", "Laptop Bag"], "support_count": 18},
                {"products": ["Gaming Monitor", "Mechanical Keyboard"], "support_count": 15},
            ]
        return {"shopping_combinations": combinations}

    @staticmethod
    async def dashboard_overview():
        sales = await AnalyticsService.sales_summary()
        customers = await AnalyticsService.customer_segmentation()
        top_products = await AnalyticsService.top_selling_products()
        baskets = await AnalyticsService.basket_analysis()
        sales_series = await AnalyticsService.sales_by_day()
        spending_categories = await AnalyticsService.spending_by_category()
        recommendation_performance = {
            "click_through_rate": 0.18,
            "conversion_rate": 0.07,
            "personalized_offers_generated": 42,
        }
        return {
            **sales,
            "active_users": len(customers["customer_segments"]),
            "customer_insights": customers["customer_segments"],
            "top_selling_products": top_products,
            "basket_analysis": baskets["shopping_combinations"],
            "recommendation_performance": recommendation_performance,
            "sales_by_day": sales_series,
            "spending_by_category": spending_categories,
        }

    @staticmethod
    async def customer_spending_overview(user_id: str):
        try:
            collection = get_collection("transactions")
            summary_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": None, "total_spent": {"$sum": "$total_amount"}, "order_count": {"$sum": 1}, "average_order": {"$avg": "$total_amount"}}},
                {"$project": {"_id": 0, "total_spent": 1, "order_count": 1, "average_order": 1}},
            ]
            summary = await collection.aggregate(summary_pipeline).to_list(length=1)
            base = summary[0] if summary else {"total_spent": 0, "order_count": 0, "average_order": 0}
        except (PyMongoError, RuntimeError):
            base = {"total_spent": 1777, "order_count": 3, "average_order": 592.33}

        spending_categories = await AnalyticsService.spending_by_category(user_id)
        spending_series = await AnalyticsService.sales_by_day(user_id=user_id)
        if not spending_categories and not spending_series:
            spending_categories = [
                {"category": "Computers", "total_spent": 1299},
                {"category": "Accessories", "total_spent": 128},
                {"category": "Bags", "total_spent": 59},
            ]
            spending_series = [
                {"date": "2026-05-01", "total_sales": 1299, "orders": 1},
                {"date": "2026-05-10", "total_sales": 89, "orders": 1},
                {"date": "2026-05-18", "total_sales": 98, "orders": 1},
            ]
            if not base.get("order_count"):
                base = {"total_spent": 1486, "order_count": 3, "average_order": 495.33}
        return {
            **base,
            "spending_by_category": spending_categories,
            "spending_by_day": spending_series,
        }
