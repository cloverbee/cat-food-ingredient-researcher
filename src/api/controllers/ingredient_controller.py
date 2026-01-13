from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.rate_limit import limiter
from src.domain.repositories.ingredient_repository import IngredientRepository
from src.domain.schemas.ingredient import IngredientCreate, IngredientRead
from src.domain.services.ingredient_service import IngredientService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_db)) -> IngredientService:
    repository = IngredientRepository(db)
    return IngredientService(repository)


@router.post("/", response_model=IngredientRead)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute", key_func=get_remote_address)
async def create_ingredient(
    request: Request,
    ingredient: IngredientCreate,
    service: IngredientService = Depends(get_service),
):
    return await service.create_ingredient(ingredient)


@router.get("/", response_model=List[IngredientRead])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute", key_func=get_remote_address)
async def read_ingredients(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    service: IngredientService = Depends(get_service),
):
    return await service.get_ingredients(skip, limit)


@router.get("/{ingredient_id}", response_model=IngredientRead)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute", key_func=get_remote_address)
async def read_ingredient(
    request: Request,
    ingredient_id: int,
    service: IngredientService = Depends(get_service),
):
    ingredient = await service.get_ingredient(ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient
