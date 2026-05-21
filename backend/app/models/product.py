from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class ProductModel(BaseModel):
    id: str | None = Field(alias="_id")
    sku: str
    name: str
    category: str
    price: float
    brand: str
    inventory_quantity: int
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
