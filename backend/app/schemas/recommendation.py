from pydantic import BaseModel
from typing import List, Dict, Optional

class UserProfile(BaseModel):
    orders: int
    total_spent: float
    top_categories: List[str]
    top_brands: List[str]
    favorite_category: Optional[str]

class RecentPurchase(BaseModel):
    product_id: str
    name: str
    quantity: int
    purchased_at: str

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Dict]
    personalized_offers: List[str]
    user_profile: UserProfile
    recent_purchases: List[RecentPurchase]

class SimilarProductsResponse(BaseModel):
    product_id: str
    similar_items: List[Dict]
