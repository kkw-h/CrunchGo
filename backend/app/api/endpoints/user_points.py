from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.user_point_log import UserPointLog
from app.schemas.user_point_log import UserPointLogResponse

router = APIRouter()

@router.get("/points", response_model=List[UserPointLogResponse])
async def read_user_points(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get user points history.
    """
    stmt = (
        select(UserPointLog)
        .where(UserPointLog.user_id == current_user.id)
        .order_by(UserPointLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return logs
