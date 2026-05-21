from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product import ProductService
from app.utils.responses import success_response
from app.services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_product(payload: ProductCreate, user=Depends(get_current_user)):
    if "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    product = await ProductService.create_product(payload)
    return product

@router.get("/", response_model=List[ProductResponse])
async def list_products():
    return await ProductService.list_products()
