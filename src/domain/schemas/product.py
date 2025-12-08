from typing import List, Optional

from pydantic import BaseModel

from src.domain.schemas.ingredient import IngredientRead


class ProductBase(BaseModel):
    name: str
    brand: str
    price: Optional[float] = None
    age_group: Optional[str] = None
    food_type: Optional[str] = None
    description: Optional[str] = None
    full_ingredient_list: Optional[str] = None


class ProductCreate(ProductBase):
    ingredient_ids: Optional[List[int]] = []


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    brand: Optional[str] = None


class ProductRead(ProductBase):
    id: int
    ingredients: List[IngredientRead] = []

    class Config:
        from_attributes = True
