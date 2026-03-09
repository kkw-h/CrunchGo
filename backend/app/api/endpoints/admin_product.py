from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
# from app.models.user import User # Removed dependency on User model for now as it lacks admin fields
from app.schemas.product import Product, ProductCreate, ProductDetail, ProductUpdate
from app.services.menu_service import MenuService

router = APIRouter()

# TODO: Implement proper admin authentication/authorization.
# Currently, these endpoints are unprotected or could use a simple API Key dependency.
# For now, we omit the dependency to avoid runtime errors with the existing User model.

@router.post("/products", response_model=ProductDetail)
async def create_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_in: ProductCreate,
    # current_user: User = Depends(deps.get_current_user), # Uncomment when admin auth is ready
) -> Any:
    """
    Create new product.
    """
    # if not current_user.is_superuser: ...
    product = await MenuService.create_product(db, product_in=product_in)
    return product

@router.put("/products/{product_id}", response_model=ProductDetail)
async def update_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_id: int,
    product_in: ProductUpdate,
    # current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a product.
    """
    product = await MenuService.update_product(db, product_id=product_id, product_in=product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/products/{product_id}", response_model=Any)
async def delete_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_id: int,
    # current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a product.
    """
    success = await MenuService.delete_product(db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "success", "message": "Product deleted successfully"}
