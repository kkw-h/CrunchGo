from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal

# --- ProductSku Schemas ---
class ProductSkuBase(BaseModel):
    specs: Optional[Dict[str, Any]] = Field(default_factory=dict, description="规格，如 {'size': 'L', 'sugar': 'half'}")
    price: Decimal = Field(..., gt=0, description="价格")
    stock_quantity: int = Field(default=0, ge=0, description="库存数量")

class ProductSkuCreate(ProductSkuBase):
    pass

class ProductSkuUpdate(ProductSkuBase):
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)

class ProductSku(ProductSkuBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    category_id: int

class ProductCreate(ProductBase):
    skus: List[ProductSkuCreate] = []

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    category_id: Optional[int] = None
    skus: Optional[List[ProductSkuCreate]] = None # Full replacement or update logic to be handled in service

class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

class ProductDetail(Product):
    skus: List[ProductSku] = []
    category_name: Optional[str] = None # Convenient for frontend

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    sort_order: int = Field(default=0)
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None

class Category(CategoryBase):
    id: int
    products: List[Product] = [] # Optional, distinct from just list of categories

    class Config:
        from_attributes = True

# Response models for lists
class CategoryList(BaseModel):
    total: int
    items: List[Category]

class ProductList(BaseModel):
    total: int
    items: List[Product]
