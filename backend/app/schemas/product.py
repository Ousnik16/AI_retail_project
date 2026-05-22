from pydantic import BaseModel, Field
from typing import List, Optional

class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    price: float
    brand: str
    inventory_quantity: int
    stock_alert_threshold: int = 10
    tags: List[str] = []

class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    inventory_quantity: Optional[int] = None
    stock_alert_threshold: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None

class ProductResponse(ProductCreate):
    id: str

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
