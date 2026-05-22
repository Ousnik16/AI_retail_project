from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import ProductService
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

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, payload: ProductUpdate, user=Depends(get_current_user)):
    if "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    product = await ProductService.update_product(product_id, payload)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: str, user=Depends(get_current_user)):
    if "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await ProductService.delete_product(product_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return result
