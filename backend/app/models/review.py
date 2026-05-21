from datetime import datetime
from pydantic import BaseModel, Field

class ReviewModel(BaseModel):
    id: str | None = Field(alias="_id")
    user_id: str
    product_id: str
    rating: int
    title: str
    review_text: str
    sentiment_score: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
