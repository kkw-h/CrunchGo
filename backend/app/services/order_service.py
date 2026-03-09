
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.redis import redis_client
from app.models.order import Order, OrderItem
from app.models.product import ProductSku, Product
from app.models.user import User
from app.models.user_point_log import UserPointLog
from app.schemas.order import OrderCreate, OrderResponse
from app.services.printer_service import PrinterService

logger = logging.getLogger(__name__)

ORDER_EXPIRATION_SECONDS = 15 * 60  # 15 minutes
REDIS_STOCK_PREFIX = "stock:sku:"
REDIS_ORDER_EXPIRE_PREFIX = "order:expire:"

class OrderService:
    @staticmethod
    async def _generate_order_no() -> str:
        # Simple order number generation: timestamp + partial uuid
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"ORD{timestamp}{unique_id}"

    @staticmethod
    async def _generate_pickup_code() -> str:
        today = datetime.now().strftime("%Y%m%d")
        key = f"daily:seq:{today}"
        seq = await redis_client.incr(key)
        if seq == 1:
            await redis_client.expire(key, 86400) # 24 hours
        return f"A{seq:03d}"

    @staticmethod
    async def create_order(db: AsyncSession, user_id: int, order_in: OrderCreate) -> Order:
        # 1. Validate items and calculate total
        # Fetch SKU details to get price and current stock info (for initial sync if needed)
        sku_ids = [item.product_sku_id for item in order_in.items]
        stmt = select(ProductSku).options(selectinload(ProductSku.product)).where(ProductSku.id.in_(sku_ids))
        result = await db.execute(stmt)
        skus = {sku.id: sku for sku in result.scalars().all()}

        if len(skus) != len(set(sku_ids)):
            raise HTTPException(status_code=400, detail="One or more products not found")

        # 2. Validate stock in Redis
        # We use a pipeline to check and decrement stock atomically for each item
        # Alternatively, use Lua script for all items at once to ensure all-or-nothing
        # For simplicity, we'll iterate and rollback if any fail, or use a Lua script.
        
        # Lua script to check and decrement multiple keys
        # Keys: stock:sku:{id1}, stock:sku:{id2}...
        # Args: qty1, qty2...
        lua_script = """
        for i, key in ipairs(KEYS) do
            local current_stock = redis.call('get', key)
            if not current_stock or tonumber(current_stock) < tonumber(ARGV[i]) then
                return -1 * i -- Return negative index of failed item
            end
        end
        for i, key in ipairs(KEYS) do
            redis.call('decrby', key, ARGV[i])
        end
        return 0
        """
        
        keys = []
        args = []
        total_amount = 0.0
        order_items_data = []

        for item in order_in.items:
            sku = skus[item.product_sku_id]
            
            # Ensure Redis has the stock key (lazy initialization)
            stock_key = f"{REDIS_STOCK_PREFIX}{sku.id}"
            await redis_client.set(stock_key, sku.stock_quantity, nx=True)
            
            keys.append(stock_key)
            args.append(item.quantity)
            
            # Prepare data for DB
            price = float(sku.price)
            total_amount += price * item.quantity
            
            # Specs snapshot
            specs_str = json.dumps(sku.specs) if sku.specs else None
            
            order_items_data.append({
                "product_sku_id": sku.id,
                "product_name_snapshot": sku.product.name,
                "specs_snapshot": specs_str,
                "price_snapshot": price,
                "quantity": item.quantity
            })

        # Execute Lua script
        result = await redis_client.eval(lua_script, len(keys), *keys, *args)
        
        if result != 0:
            failed_index = -1 * result - 1
            failed_sku_id = sku_ids[failed_index]
            raise HTTPException(status_code=400, detail=f"Insufficient stock for SKU ID {failed_sku_id}")

        try:
            # 3. Create Order in DB
            order_no = await OrderService._generate_order_no()
            pickup_code = await OrderService._generate_pickup_code() if order_in.type == "PICKUP" else None
            
            new_order = Order(
                order_no=order_no,
                user_id=user_id,
                total_amount=total_amount,
                status="PENDING",
                type=order_in.type,
                pickup_code=pickup_code
            )
            db.add(new_order)
            
            for item_data in order_items_data:
                new_item = OrderItem(
                    order_no=new_order.order_no,
                    **item_data
                )
                db.add(new_item)
                
                # Update DB stock as well to keep in sync (eventual consistency or best effort)
                # We find the sku object from our earlier fetch
                sku = skus[item_data["product_sku_id"]]
                sku.stock_quantity -= item_data["quantity"]
                db.add(sku)
            
            await db.commit()
            await db.refresh(new_order)
            
            # Eager load items for response
            stmt = select(Order).options(selectinload(Order.items)).where(Order.order_no == order_no)
            result = await db.execute(stmt)
            final_order = result.scalars().first()

            # 4. Set Redis expiration
            expire_key = f"{REDIS_ORDER_EXPIRE_PREFIX}{order_no}"
            await redis_client.setex(expire_key, ORDER_EXPIRATION_SECONDS, "pending")
            
            return final_order

        except Exception as e:
            # Rollback Redis stock if DB fails
            logger.error(f"Error creating order: {e}")
            for i, key in enumerate(keys):
                await redis_client.incrby(key, args[i])
            raise e

    @staticmethod
    async def get_order(db: AsyncSession, order_no: str, user_id: int) -> Order:
        stmt = select(Order).options(selectinload(Order.items)).where(Order.order_no == order_no)
        result = await db.execute(stmt)
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this order")
            
        return order

    @staticmethod
    async def cancel_order(db: AsyncSession, order_no: str, user_id: int) -> Order:
        # Fetch order with items to restore stock
        stmt = select(Order).options(selectinload(Order.items)).where(Order.order_no == order_no)
        result = await db.execute(stmt)
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
        
        if order.status != "PENDING":
            raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
            
        # Update status
        order.status = "CANCELLED"
        await db.commit()
        await db.refresh(order)
        
        # Restore stock in Redis
        for item in order.items:
            stock_key = f"{REDIS_STOCK_PREFIX}{item.product_sku_id}"
            await redis_client.incrby(stock_key, item.quantity)
            
        # Remove expiration key
        expire_key = f"{REDIS_ORDER_EXPIRE_PREFIX}{order_no}"
        await redis_client.delete(expire_key)
        
        return order
        
    @staticmethod
    async def pay_order(db: AsyncSession, order_no: str, user_id: int) -> Order:
        order = await OrderService.get_order(db, order_no, user_id)
        
        if order.status != "PENDING":
             raise HTTPException(status_code=400, detail="Order is not in pending state")
             
        # Mock payment success
        order.status = "PAID"
        
        # Calculate points (1 CNY = 1 Point)
        points_earned = int(order.total_amount)
        if points_earned > 0:
            # Fetch user to update balance
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalars().first()
            
            if user:
                user.point_balance += points_earned
                db.add(user)
                
                point_log = UserPointLog(
                    user_id=user_id,
                    points=points_earned,
                    description=f"Order #{order_no}",
                    type="EARN"
                )
                db.add(point_log)
                logger.info(f"Awarded {points_earned} points to user {user_id} for order {order_no}")

        await db.commit()
        await db.refresh(order)
        
        # Remove expiration key as it is now paid
        expire_key = f"{REDIS_ORDER_EXPIRE_PREFIX}{order_no}"
        await redis_client.delete(expire_key)
        
        # Print receipt
        try:
            await PrinterService.print_order(order)
        except Exception as e:
            logger.error(f"Failed to trigger print job for order {order_no}: {e}")

        return order

    @staticmethod
    async def refund_order_request(db: AsyncSession, order_no: str, user_id: int) -> Order:
        stmt = select(Order).options(selectinload(Order.items)).where(Order.order_no == order_no)
        result = await db.execute(stmt)
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to request refund for this order")
        
        # Check if status is PAID or PREPARING
        if order.status not in ["PAID", "PREPARING"]:
            raise HTTPException(status_code=400, detail="Only PAID or PREPARING orders can be refunded")
            
        order.status = "REFUNDING"
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def approve_refund(db: AsyncSession, order_no: str) -> Order:
        stmt = select(Order).options(selectinload(Order.items)).where(Order.order_no == order_no)
        result = await db.execute(stmt)
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != "REFUNDING":
            raise HTTPException(status_code=400, detail="Order is not in REFUNDING state")
            
        # Mock WeChat Refund API
        logger.info(f"Mocking WeChat Refund for order {order_no}, amount: {order.total_amount}")
        
        # Update status
        order.status = "REFUNDED"
        
        # Restore stock if PREPARING (not cooked).
        # Since we are in REFUNDING state, we assume valid refund implies restoring stock 
        # (as strictly per prompt "Restore stock if PREPARING").
        # We'll implement stock restoration.
        for item in order.items:
            # Restore Redis stock
            stock_key = f"{REDIS_STOCK_PREFIX}{item.product_sku_id}"
            await redis_client.incrby(stock_key, item.quantity)
            
            # Restore DB stock
            sku_stmt = select(ProductSku).where(ProductSku.id == item.product_sku_id)
            sku_res = await db.execute(sku_stmt)
            sku = sku_res.scalars().first()
            if sku:
                sku.stock_quantity += item.quantity
                db.add(sku)
                
        await db.commit()
        await db.refresh(order)
        return order

