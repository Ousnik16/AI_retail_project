from pydantic import BaseModel
from typing import List, Optional

class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    price: float
    brand: str
    inventory_quantity: int
    tags: List[str] = []

class ProductResponse(ProductCreate):
    id: str

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
