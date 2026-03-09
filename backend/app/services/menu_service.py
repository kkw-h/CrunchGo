from typing import List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete
from sqlalchemy.orm import selectinload

from app.models.product import Category, Product, ProductSku
from app.schemas.product import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate

class MenuService:
    
    # --- Category Operations ---
    @staticmethod
    async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
        stmt = select(Category).where(Category.is_active == True).order_by(Category.sort_order).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_category(db: AsyncSession, category_id: int) -> Optional[Category]:
        return await db.get(Category, category_id)

    @staticmethod
    async def create_category(db: AsyncSession, category_in: CategoryCreate) -> Category:
        category = Category(**category_in.dict())
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def update_category(db: AsyncSession, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
        category = await MenuService.get_category(db, category_id)
        if not category:
            return None
        
        update_data = category_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
            
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> bool:
        category = await MenuService.get_category(db, category_id)
        if not category:
            return False
        await db.delete(category)
        await db.commit()
        return True

    # --- Product Operations ---
    @staticmethod
    async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100, category_id: Optional[int] = None) -> List[Product]:
        stmt = select(Product).where(Product.is_active == True).options(selectinload(Product.skus))
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        stmt = stmt.order_by(Product.id.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int) -> Optional[Product]:
        stmt = select(Product).where(Product.id == product_id).options(selectinload(Product.skus))
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
        # Create Product
        product_data = product_in.dict(exclude={"skus"})
        product = Product(**product_data)
        db.add(product)
        await db.flush() # Get ID

        # Create SKUs
        if product_in.skus:
            for sku_data in product_in.skus:
                sku = ProductSku(**sku_data.dict(), product_id=product.id)
                db.add(sku)
        
        await db.commit()
        await db.refresh(product)
        # Re-fetch with SKUs to ensure consistent return
        return await MenuService.get_product(db, product.id)

    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, product_in: ProductUpdate) -> Optional[Product]:
        product = await MenuService.get_product(db, product_id)
        if not product:
            return None

        # Update Product Fields
        update_data = product_in.dict(exclude_unset=True, exclude={"skus"})
        for field, value in update_data.items():
            setattr(product, field, value)

        # Update SKUs (Full Replacement Strategy)
        if product_in.skus is not None:
            # Delete existing SKUs
            stmt = delete(ProductSku).where(ProductSku.product_id == product.id)
            await db.execute(stmt)
            
            # Add new SKUs
            for sku_data in product_in.skus:
                sku = ProductSku(**sku_data.dict(), product_id=product.id)
                db.add(sku)

        db.add(product)
        await db.commit()
        await db.refresh(product)
        return await MenuService.get_product(db, product.id)

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int) -> bool:
        product = await MenuService.get_product(db, product_id)
        if not product:
            return False
        
        # Manual cascade delete for SKUs
        stmt = delete(ProductSku).where(ProductSku.product_id == product.id)
        await db.execute(stmt)
        
        await db.delete(product)
        await db.commit()
        return True
