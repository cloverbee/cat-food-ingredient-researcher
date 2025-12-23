from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base

# Association Table
product_ingredient_association = Table(
    "product_ingredient_association",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("cat_food_product.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredient.id"), primary_key=True),
)


class CatFoodProduct(Base):
    __tablename__ = "cat_food_product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    brand = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=True)
    age_group = Column(String, index=True, nullable=True)  # kitten, adult, senior
    food_type = Column(String, index=True, nullable=True)  # wet, dry
    description = Column(Text, nullable=True)
    full_ingredient_list = Column(Text, nullable=True)  # Raw text of ingredients
    image_url = Column(String, nullable=True)  # Product image URL
    shopping_url = Column(String, nullable=True)  # Affiliate/shopping link to purchase

    # Qdrant Point ID (UUID stored as string)
    embedding_id = Column(String, nullable=True)

    ingredients = relationship("Ingredient", secondary=product_ingredient_association, back_populates="products")
