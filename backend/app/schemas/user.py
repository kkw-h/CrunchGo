from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    openid: str
    nickname: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    id: int
    point_balance: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
