from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class TransactionModel(BaseModel):
    id: str | None = Field(alias="_id")
    user_id: str
    products: List[dict]
    total_amount: float
    purchased_at: datetime = Field(default_factory=datetime.utcnow)
    channel: str = "online"
    status: str = "completed"

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
