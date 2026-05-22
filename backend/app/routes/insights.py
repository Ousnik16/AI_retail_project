from fastapi import APIRouter, Depends
from app.services.llm_insights import LLMInsightsService
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/summary")
async def retail_summary(question: str = "Generate a monthly retail summary", user=Depends(get_current_user)):
    return await LLMInsightsService.generate_insight(question, user)
