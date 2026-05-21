from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional

class TransactionItem(BaseModel):
    product_id: str
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: int
    unit_price: float

class TransactionCreate(BaseModel):
    user_id: str
    items: List[TransactionItem]
    channel: str = "online"

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    products: List[Dict]
    total_amount: float
    purchased_at: datetime
    status: str

class BrowsingEventCreate(BaseModel):
    user_id: str
    product_id: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    event_type: str = "view"
    session_id: Optional[str] = None

class InventoryUpdate(BaseModel):
    product_id: str
    quantity_delta: int
