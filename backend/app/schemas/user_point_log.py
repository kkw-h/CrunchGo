from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class UserPointLogBase(BaseModel):
    points: int
    description: Optional[str] = None
    type: str

class UserPointLogCreate(UserPointLogBase):
    pass

class UserPointLogResponse(UserPointLogBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
