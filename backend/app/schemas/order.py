
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class OrderItemSchema(BaseModel):
    product_sku_id: int
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    items: List[OrderItemSchema]
    type: str  # DINE_IN, PICKUP

class OrderItemResponse(BaseModel):
    id: int
    product_sku_id: Optional[int]
    product_name_snapshot: str
    specs_snapshot: Optional[str]
    price_snapshot: float
    quantity: int

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    order_no: str
    user_id: int
    total_amount: float
    status: str
    pickup_code: Optional[str]
    type: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
