from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class IngredientBase(BaseModel):
    name: str
    description: Optional[str] = None
    nutritional_value: Optional[Dict[str, Any]] = None
    common_allergens: Optional[List[str]] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(IngredientBase):
    name: Optional[str] = None

class IngredientRead(IngredientBase):
    id: int

    class Config:
        from_attributes = True
