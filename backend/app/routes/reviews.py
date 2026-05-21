from fastapi import APIRouter, Depends
from app.services.sentiment import SentimentService
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/sentiment")
async def review_sentiment(user=Depends(get_current_user)):
    return await SentimentService.analyze_reviews()
