from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.product import Category, Product, ProductDetail
from app.services.menu_service import MenuService

router = APIRouter()

@router.get("/categories", response_model=List[Category])
async def read_categories(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all categories.
    """
    categories = await MenuService.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/products", response_model=List[Product])
async def read_products(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
):
    """
    Get all products, optionally filtered by category.
    """
    products = await MenuService.get_products(db, skip=skip, limit=limit, category_id=category_id)
    return products

@router.get("/products/{product_id}", response_model=ProductDetail)
async def read_product(
    product_id: int,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Get product by ID with details (SKUs).
    """
    product = await MenuService.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product
