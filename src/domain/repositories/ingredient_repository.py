from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.ingredient import Ingredient
from src.domain.schemas.ingredient import IngredientCreate, IngredientUpdate


class IngredientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, ingredient: IngredientCreate) -> Ingredient:
        db_ingredient = Ingredient(**ingredient.model_dump())
        self.db.add(db_ingredient)
        await self.db.commit()
        await self.db.refresh(db_ingredient)
        return db_ingredient

    async def get(self, ingredient_id: int) -> Optional[Ingredient]:
        result = await self.db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Ingredient]:
        result = await self.db.execute(select(Ingredient).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_name(self, name: str) -> Optional[Ingredient]:
        result = await self.db.execute(select(Ingredient).where(Ingredient.name == name))
        return result.scalars().first()
