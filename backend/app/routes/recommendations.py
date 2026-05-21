from fastapi import APIRouter, Depends
from app.services.recommendations import RecommendationService
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/user/{user_id}")
async def personalized_recommendations(user_id: str, user=Depends(get_current_user)):
    return await RecommendationService.user_recommendations(user_id)

@router.get("/product/{product_id}")
async def similar_products(product_id: str, user=Depends(get_current_user)):
    return await RecommendationService.similar_products(product_id)
