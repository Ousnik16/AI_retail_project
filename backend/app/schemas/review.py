from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(ge=1, le=5)
    title: str
    review_text: str


class ReviewResponse(ReviewCreate):
    id: str
    user_id: str
    created_at: str
