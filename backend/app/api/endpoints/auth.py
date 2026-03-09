from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.services.user_service import user_service
from app.core.database import get_db

router = APIRouter()

@router.post("/login/wechat", response_model=Token)
async def login_wechat(
    code: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    WeChat Login.
    """
    user = await user_service.authenticate_wechat(db=db, code=code)
    
    if not user:
        raise HTTPException(status_code=400, detail="Authentication failed")
    
    access_token = security.create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
