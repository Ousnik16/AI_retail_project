from pydantic import BaseModel
from typing import List, Dict

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Dict]

class SimilarProductsResponse(BaseModel):
    product_id: str
    similar_items: List[Dict]
