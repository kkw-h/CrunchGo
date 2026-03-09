from fastapi import APIRouter
from app.api.endpoints import auth, menu, admin_product, order, user_points, admin_order, stats

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
api_router.include_router(admin_product.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_order.router, prefix="/admin/orders", tags=["admin-orders"])
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
api_router.include_router(user_points.router, prefix="/user", tags=["user"])
api_router.include_router(stats.router, prefix="/admin/stats", tags=["admin-stats"])
