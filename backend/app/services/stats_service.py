from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, time
from app.models.order import Order, OrderItem
from app.models.product import Product, ProductSku

class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_sales(self) -> float:
        """
        Query Orders (status=PAID/COMPLETED/PREPARING) for today. Sum total_amount.
        """
        today_start = datetime.combine(datetime.now().date(), time.min)
        today_end = datetime.combine(datetime.now().date(), time.max)
        
        # Valid sales statuses: PAID, PREPARING, COMPLETED
        # Exclude: PENDING (not paid), CANCELLED (not paid), REFUNDED (money returned), REFUNDING (in process of return)
        valid_statuses = ['PAID', 'PREPARING', 'COMPLETED']
        
        query = select(func.sum(Order.total_amount)).where(
            and_(
                Order.created_at >= today_start,
                Order.created_at <= today_end,
                Order.status.in_(valid_statuses)
            )
        )
        result = await self.db.execute(query)
        return float(result.scalar() or 0.0)

    async def get_daily_order_count(self) -> int:
        """
        Count valid orders today.
        """
        today_start = datetime.combine(datetime.now().date(), time.min)
        today_end = datetime.combine(datetime.now().date(), time.max)
        
        valid_statuses = ['PAID', 'PREPARING', 'COMPLETED']
        
        query = select(func.count(Order.order_no)).where(
            and_(
                Order.created_at >= today_start,
                Order.created_at <= today_end,
                Order.status.in_(valid_statuses)
            )
        )
        result = await self.db.execute(query)
        return int(result.scalar() or 0)

    async def get_top_products(self, limit: int = 5):
        """
        Query OrderItems joined with Products, group by product_id, sum quantity, order by desc. Limit 5.
        Counts all-time sales for valid orders.
        """
        valid_statuses = ['PAID', 'PREPARING', 'COMPLETED', 'COMPLETED'] # Added COMPLETED twice by mistake, removing one
        valid_statuses = ['PAID', 'PREPARING', 'COMPLETED']

        query = select(
            Product.name,
            func.sum(OrderItem.quantity).label('total_quantity')
        ).join(
            Order, OrderItem.order_no == Order.order_no
        ).join(
            ProductSku, OrderItem.product_sku_id == ProductSku.id
        ).join(
            Product, ProductSku.product_id == Product.id
        ).where(
            Order.status.in_(valid_statuses)
        ).group_by(
            Product.id, Product.name
        ).order_by(
            desc('total_quantity')
        ).limit(limit)
        
        result = await self.db.execute(query)
        return [{"name": row.name, "quantity": int(row.total_quantity)} for row in result.all()]
