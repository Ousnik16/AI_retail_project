from fastapi import APIRouter, Depends
from app.services.analytics import AnalyticsService
from app.services.auth import get_current_user

router = APIRouter()

@router.get("/customers")
async def customer_insights(user=Depends(get_current_user)):
    return await AnalyticsService.customer_segmentation()

@router.get("/sales")
async def sales_summary(user=Depends(get_current_user)):
    return await AnalyticsService.sales_summary()

@router.get("/dashboard")
async def dashboard_overview(user=Depends(get_current_user)):
    return await AnalyticsService.dashboard_overview()

@router.get("/top-products")
async def top_products(user=Depends(get_current_user)):
    return {"products": await AnalyticsService.top_selling_products()}

@router.get("/basket")
async def basket_analysis(user=Depends(get_current_user)):
    return await AnalyticsService.basket_analysis()
