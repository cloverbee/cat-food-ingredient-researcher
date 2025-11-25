from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domain.models.product import CatFoodProduct
from src.domain.models.ingredient import Ingredient
from src.domain.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: ProductCreate) -> CatFoodProduct:
        db_product = CatFoodProduct(
            name=product.name,
            brand=product.brand,
            price=product.price,
            age_group=product.age_group,
            food_type=product.food_type,
            description=product.description,
            full_ingredient_list=product.full_ingredient_list
        )
        
        if product.ingredient_ids:
            stmt = select(Ingredient).where(Ingredient.id.in_(product.ingredient_ids))
            result = await self.db.execute(stmt)
            ingredients = result.scalars().all()
            db_product.ingredients = ingredients

        self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        # Eager load ingredients for return
        await self.db.refresh(db_product, attribute_names=["ingredients"])
        return db_product

    async def get(self, product_id: int) -> Optional[CatFoodProduct]:
        result = await self.db.execute(
            select(CatFoodProduct)
            .options(selectinload(CatFoodProduct.ingredients))
            .where(CatFoodProduct.id == product_id)
        )
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CatFoodProduct]:
        result = await self.db.execute(
            select(CatFoodProduct)
            .options(selectinload(CatFoodProduct.ingredients))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
