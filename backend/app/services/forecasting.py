from app.db.database import get_collection
from datetime import datetime, timedelta
import pandas as pd
from pymongo.errors import PyMongoError

class ForecastService:
    @staticmethod
    async def product_forecast(product_id: str):
        records = []
        try:
            collection = get_collection("transactions")
            cursor = collection.find({"products.product_id": product_id})
            async for tx in cursor:
                for item in tx["products"]:
                    if item["product_id"] == product_id:
                        records.append({"ds": tx["purchased_at"], "y": item["quantity"]})
        except (PyMongoError, RuntimeError):
            records = []
        if not records:
            today = datetime.utcnow().date()
            return {
                "product_id": product_id,
                "forecast": [
                    {
                        "ds": datetime.combine(today + timedelta(days=day), datetime.min.time()),
                        "yhat": 8 + day * 0.6,
                        "yhat_lower": 6 + day * 0.4,
                        "yhat_upper": 11 + day * 0.8,
                    }
                    for day in range(1, 15)
                ],
                "method": "moving-average-demo",
            }
        df = pd.DataFrame(records)
        daily = df.groupby(pd.to_datetime(df["ds"]).dt.date)["y"].sum().tail(14)
        baseline = float(daily.mean())
        return {
            "product_id": product_id,
            "forecast": [
                {
                    "ds": datetime.combine(datetime.utcnow().date() + timedelta(days=day), datetime.min.time()),
                    "yhat": baseline,
                    "yhat_lower": max(0, baseline * 0.8),
                    "yhat_upper": baseline * 1.2,
                }
                for day in range(1, 15)
            ],
            "method": "moving-average",
        }
