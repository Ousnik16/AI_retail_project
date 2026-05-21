from datetime import datetime
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from app.db.database import get_collection
from app.schemas.transaction import BrowsingEventCreate, InventoryUpdate, TransactionCreate
from pymongo.errors import PyMongoError
from uuid import uuid4

LIVE_EVENTS = []


def _api_safe(value):
    return jsonable_encoder(value, custom_encoder={ObjectId: str})


def _push_event(event_type: str, payload: dict) -> dict:
    event = {"type": event_type, "payload": _api_safe(payload), "created_at": datetime.utcnow()}
    LIVE_EVENTS.insert(0, event)
    del LIVE_EVENTS[50:]
    return event

class TransactionService:
    @staticmethod
    async def create_transaction(payload: TransactionCreate):
        items = [
            {
                "product_id": item.product_id,
                "name": item.name or item.product_id.replace("-", " ").title(),
                "category": item.category or "General",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total": item.quantity * item.unit_price,
            }
            for item in payload.items
        ]
        total_amount = sum(item["total"] for item in items)
        document = {
            "user_id": payload.user_id,
            "products": items,
            "total_amount": total_amount,
            "purchased_at": datetime.utcnow(),
            "channel": payload.channel,
            "status": "completed",
        }
        try:
            collection = get_collection("transactions")
            result = await collection.insert_one(document)
            saved = {"id": str(result.inserted_id), **{k: v for k, v in document.items() if k != "_id"}}
        except (PyMongoError, RuntimeError):
            saved = {"id": f"offline-{uuid4().hex[:10]}", **document}
        await TransactionService.apply_inventory_updates(
            [InventoryUpdate(product_id=item["product_id"], quantity_delta=-item["quantity"]) for item in items]
        )
        _push_event("transaction_ingested", saved)
        return _api_safe(saved)

    @staticmethod
    async def get_user_transactions(user_id: str):
        transactions = []
        try:
            collection = get_collection("transactions")
            cursor = collection.find({"user_id": user_id}).sort("purchased_at", -1)
            async for tx in cursor:
                transactions.append(_api_safe({"id": str(tx["_id"]), **{k: v for k, v in tx.items() if k != "_id"}}))
        except (PyMongoError, RuntimeError):
            transactions = []
        return transactions

    @staticmethod
    async def create_online_order(payload: TransactionCreate):
        payload.channel = "online"
        order = await TransactionService.create_transaction(payload)
        _push_event("online_order_analyzed", {"order_id": order["id"], "total_amount": order["total_amount"]})
        return order

    @staticmethod
    async def record_browsing_event(payload: BrowsingEventCreate):
        document = {**payload.dict(), "created_at": datetime.utcnow()}
        try:
            collection = get_collection("browsing_history")
            result = await collection.insert_one(document)
            saved = {"id": str(result.inserted_id), **{k: v for k, v in document.items() if k != "_id"}}
        except (PyMongoError, RuntimeError):
            saved = {"id": f"offline-{uuid4().hex[:10]}", **document}
        _push_event("product_browsed", saved)
        return _api_safe(saved)

    @staticmethod
    async def apply_inventory_updates(updates: list[InventoryUpdate]):
        applied = []
        for update in updates:
            try:
                products = get_collection("products")
                result = await products.update_one(
                    {"$or": [{"_id": update.product_id}, {"sku": update.product_id}]},
                    {"$inc": {"inventory_quantity": update.quantity_delta}},
                )
                matched = result.matched_count
            except (PyMongoError, RuntimeError):
                matched = 0
            applied.append({"product_id": update.product_id, "quantity_delta": update.quantity_delta, "matched": matched})
        _push_event("inventory_updated", {"updates": applied})
        return {"updates": applied}

    @staticmethod
    async def recent_events():
        return {"events": _api_safe(LIVE_EVENTS)}
