from src.domain.repositories.ingredient_repository import IngredientRepository
from src.domain.schemas.ingredient import IngredientCreate, IngredientRead
from typing import List, Optional

class IngredientService:
    def __init__(self, repository: IngredientRepository):
        self.repository = repository

    async def create_ingredient(self, ingredient: IngredientCreate) -> IngredientRead:
        return await self.repository.create(ingredient)

    async def get_ingredient(self, ingredient_id: int) -> Optional[IngredientRead]:
        return await self.repository.get(ingredient_id)

    async def get_ingredients(self, skip: int = 0, limit: int = 100) -> List[IngredientRead]:
        return await self.repository.get_all(skip, limit)
