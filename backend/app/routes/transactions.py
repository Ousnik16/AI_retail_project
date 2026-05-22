from fastapi import APIRouter, HTTPException, status
import random
from datetime import datetime, timedelta
from app.schemas.transaction import BrowsingEventCreate, InventoryUpdate, TransactionCreate, TransactionResponse
from app.services.transaction import TransactionService
from app.schemas.transaction import TransactionItem, TransactionCreate
from app.db.database import get_collection

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(payload: TransactionCreate):
    transaction = await TransactionService.create_transaction(payload)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save transaction")
    return transaction

@router.post("/ingest", response_model=TransactionResponse)
async def ingest_live_transaction(payload: TransactionCreate):
    return await TransactionService.create_transaction(payload)

@router.post("/orders", response_model=TransactionResponse)
async def ingest_online_order(payload: TransactionCreate):
    return await TransactionService.create_online_order(payload)

@router.post("/browse")
async def ingest_browsing_event(payload: BrowsingEventCreate):
    return await TransactionService.record_browsing_event(payload)

@router.post("/inventory")
async def update_inventory(updates: list[InventoryUpdate]):
    return await TransactionService.apply_inventory_updates(updates)

@router.get("/stream-events")
async def stream_events():
    return await TransactionService.recent_events()

@router.get("/history", response_model=list[TransactionResponse])
async def transaction_history(user_id: str):
    return await TransactionService.get_user_transactions(user_id)


@router.post("/seed/{user_id}")
async def seed_user_history(user_id: str, count: int = 5):
    """Create `count` synthetic transactions for `user_id` using available products.

    Automatically seeds sample products if collection is empty to ensure diversity for recommendations.
    """
    try:
        products_coll = get_collection("products")
        products = await products_coll.find({}).to_list(length=100)
        
        # If no products exist, seed sample products into the collection to ensure recommendation diversity
        if not products:
            sample_products = [
                {"sku": "LAPTOP-001", "name": "Laptop Pro", "category": "electronics", "price": 1299.0, "brand": "TechBrand", "inventory_quantity": 10, "tags": ["laptop", "computer"]},
                {"sku": "MOUSE-001", "name": "Wireless Mouse", "category": "accessories", "price": 29.99, "brand": "TechBrand", "inventory_quantity": 50, "tags": ["mouse", "wireless"]},
                {"sku": "MONITOR-001", "name": "Gaming Monitor", "category": "electronics", "price": 299.0, "brand": "DisplayCo", "inventory_quantity": 15, "tags": ["monitor", "gaming"]},
                {"sku": "KEYBOARD-001", "name": "Mechanical Keyboard", "category": "accessories", "price": 89.99, "brand": "KeyMaker", "inventory_quantity": 30, "tags": ["keyboard", "gaming"]},
                {"sku": "HEADPHONES-001", "name": "Noise Cancelling Headphones", "category": "audio", "price": 179.0, "brand": "AudioPro", "inventory_quantity": 20, "tags": ["headphones", "audio"]},
                {"sku": "CABLE-001", "name": "USB-C Cable", "category": "accessories", "price": 12.99, "brand": "ConnectCo", "inventory_quantity": 100, "tags": ["cable", "usb-c"]},
                {"sku": "TABLET-001", "name": "Tablet Ultra", "category": "electronics", "price": 599.0, "brand": "TechBrand", "inventory_quantity": 12, "tags": ["tablet", "portable"]},
                {"sku": "CASE-001", "name": "Laptop Case", "category": "accessories", "price": 49.99, "brand": "CarryCo", "inventory_quantity": 40, "tags": ["case", "protection"]},
            ]
            await products_coll.insert_many(sample_products)
            products = sample_products
        
        created = []
        for i in range(count):
            # pick 1-3 products per transaction
            picks = random.sample(products, k=min(len(products), random.randint(1, 3)))
            items = [
                TransactionItem(
                    product_id=prod.get("sku") or prod.get("id"),
                    name=prod.get("name"),
                    category=prod.get("category"),
                    quantity=random.randint(1, 2),
                    unit_price=float(prod.get("price") or 0.0),
                )
                for prod in picks
            ]
            payload = TransactionCreate(user_id=user_id, items=items, channel="online")
            tx = await TransactionService.create_transaction(payload)
            # ensure timestamps are spread out
            if isinstance(tx, dict) and tx.get("purchased_at"):
                created.append(tx)
        return {"created": len(created), "user_id": user_id, "products_in_catalog": len(products)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/user/{user_id}")
async def get_user_transactions(user_id: str):
    """Return transactions for a user (convenience endpoint for debugging).

    Use this to confirm transactions were stored for `user_id`.
    """
    txs = await TransactionService.get_user_transactions(user_id)
    return {"user_id": user_id, "transactions": txs, "count": len(txs)}
