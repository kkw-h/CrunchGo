
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    order_in: OrderCreate,
) -> Any:
    """
    Create new order.
    """
    order = await OrderService.create_order(db=db, user_id=current_user.id, order_in=order_in)
    return order

@router.get("/{order_no}", response_model=OrderResponse)
async def get_order(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    order_no: str,
) -> Any:
    """
    Get order by order_no.
    """
    order = await OrderService.get_order(db=db, order_no=order_no, user_id=current_user.id)
    return order

@router.post("/{order_no}/pay", response_model=OrderResponse)
async def pay_order(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    order_no: str,
) -> Any:
    """
    Pay for an order.
    """
    order = await OrderService.pay_order(db=db, order_no=order_no, user_id=current_user.id)
    return order

@router.post("/{order_no}/cancel", response_model=OrderResponse)
async def cancel_order(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    order_no: str,
) -> Any:
    """
    Cancel an order.
    """
    order = await OrderService.cancel_order(db=db, order_no=order_no, user_id=current_user.id)
    return order

@router.post("/{order_no}/refund", response_model=OrderResponse)
async def refund_order_request(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    order_no: str,
) -> Any:
    """
    Request a refund for an order.
    """
    order = await OrderService.refund_order_request(db=db, order_no=order_no, user_id=current_user.id)
    return order
