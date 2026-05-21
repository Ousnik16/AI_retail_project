from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.transaction import BrowsingEventCreate, InventoryUpdate, TransactionCreate, TransactionResponse
from app.services.transaction import TransactionService
from app.services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(payload: TransactionCreate, user=Depends(get_current_user)):
    transaction = await TransactionService.create_transaction(payload)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save transaction")
    return transaction

@router.post("/ingest", response_model=TransactionResponse)
async def ingest_live_transaction(payload: TransactionCreate, user=Depends(get_current_user)):
    return await TransactionService.create_transaction(payload)

@router.post("/orders", response_model=TransactionResponse)
async def ingest_online_order(payload: TransactionCreate, user=Depends(get_current_user)):
    return await TransactionService.create_online_order(payload)

@router.post("/browse")
async def ingest_browsing_event(payload: BrowsingEventCreate, user=Depends(get_current_user)):
    return await TransactionService.record_browsing_event(payload)

@router.post("/inventory")
async def update_inventory(updates: list[InventoryUpdate], user=Depends(get_current_user)):
    return await TransactionService.apply_inventory_updates(updates)

@router.get("/stream-events")
async def stream_events(user=Depends(get_current_user)):
    return await TransactionService.recent_events()

@router.get("/history", response_model=list[TransactionResponse])
async def transaction_history(user=Depends(get_current_user)):
    return await TransactionService.get_user_transactions(user["user_id"])
