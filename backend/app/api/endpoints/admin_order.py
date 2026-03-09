from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_db
from app.schemas.order import OrderResponse
from app.services.order_service import OrderService

router = APIRouter()

# TODO: Implement proper admin authentication/authorization.

@router.post("/{order_no}/refund/approve", response_model=OrderResponse)
async def approve_refund(
    *,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(deps.get_current_admin_user), # Placeholder
    order_no: str,
) -> Any:
    """
    Approve an order refund.
    """
    order = await OrderService.approve_refund(db=db, order_no=order_no)
    return order
