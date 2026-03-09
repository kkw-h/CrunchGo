from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.stats_service import StatsService

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    service = StatsService(db)
    
    daily_sales = await service.get_daily_sales()
    daily_order_count = await service.get_daily_order_count()
    top_products = await service.get_top_products()
    
    return {
        "daily_sales": daily_sales,
        "daily_order_count": daily_order_count,
        "top_products": top_products
    }
