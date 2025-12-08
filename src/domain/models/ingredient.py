from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class Ingredient(Base):
    __tablename__ = "ingredient"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    nutritional_value = Column(JSONB, nullable=True)  # e.g. {"protein": "10%"}
    common_allergens = Column(JSONB, nullable=True)  # e.g. ["chicken", "grain"]

    # Relationship with products (Many-to-Many)
    products = relationship("CatFoodProduct", secondary="product_ingredient_association", back_populates="ingredients")
