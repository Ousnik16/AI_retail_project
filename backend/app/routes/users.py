from fastapi import APIRouter, Depends
from app.services.auth import get_current_user
from app.utils.responses import success_response

router = APIRouter()

@router.get("/me")
async def read_current_user(user=Depends(get_current_user)):
    return success_response("Current user retrieved", user)
