from fastapi import APIRouter, Query
from app.services.recommendations import RecommendationService
from app.schemas.recommendation import RecommendationResponse

router = APIRouter()

@router.get("/user/{user_id}", response_model=RecommendationResponse)
async def personalized_recommendations(user_id: str, debug: bool = Query(False, description="Return diagnostics instead of only recommendations")):
    return await RecommendationService.user_recommendations(user_id, debug=debug)

@router.get("/product/{product_id}")
async def similar_products(product_id: str):
    return await RecommendationService.similar_products(product_id)
