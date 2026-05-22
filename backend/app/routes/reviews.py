from fastapi import APIRouter, Depends, HTTPException, status
from app.services.sentiment import SentimentService
from app.services.auth import get_current_user
from app.services.llm_insights import LLMInsightsService
from app.services.reviews import ReviewService
from app.schemas.review import ReviewCreate

router = APIRouter()

@router.post("/")
async def create_review(payload: ReviewCreate, user=Depends(get_current_user)):
    roles = user.get("roles", [])
    if "customer" not in roles or "admin" in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only customers can submit reviews")

    if not payload.title.strip() or not payload.review_text.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title and review text are required")

    return await ReviewService.create_review(payload, user)

@router.get("/sentiment")
async def review_sentiment(user_id: str | None = None, user=Depends(get_current_user)):
    if "admin" not in user.get("roles", []):
        user_id = user.get("email") or user.get("user_id")
    return await SentimentService.analyze_reviews(user_id)


@router.get("/insights")
async def review_insights(question: str = "Summarize review-driven business actions", user_id: str | None = None, user=Depends(get_current_user)):
    if "admin" not in user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return await LLMInsightsService.generate_review_insight(question, user_id)
