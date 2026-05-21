from fastapi import APIRouter, Depends
from app.services.forecasting import ForecastService
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/product/{product_id}")
async def forecast_product_demand(product_id: str, user=Depends(get_current_user)):
    return await ForecastService.product_forecast(product_id)
