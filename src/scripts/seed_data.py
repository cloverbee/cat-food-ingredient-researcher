import asyncio
import os

import qdrant_client
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from sqlalchemy import select

from src.core.config import settings
from src.core.database import AsyncSessionLocal, Base, engine
from src.domain.models.ingredient import Ingredient
from src.domain.models.product import CatFoodProduct
from src.infrastructure.ai.llama_index_config import configure_llama_index

# Configure LlamaIndex
configure_llama_index()


async def seed_data():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        print("Clearing existing data...")
        await session.execute(select(CatFoodProduct))  # Just to check connection, real delete below
        # Note: In a real prod env, be careful with drop_all or delete.
        # For seed, we might want to just add if not exists, or clear.
        # Let's clear for now to ensure clean state as per plan.
        # We need to delete products first because of foreign keys if any,
        # but here the association table handles it.

        # Delete all data
        # We need to delete from association table first, but SQLAlchemy handles cascade if configured.
        # However, let's just drop and recreate tables for a clean slate which is easier for seed script
        pass

    # Re-create tables to clear data (easiest way for seed script)
    print("Re-creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        print("Seeding ingredients...")
        ingredients_data = [
            {
                "name": "Chicken",
                "description": "High-quality protein source.",
                "nutritional_value": {"protein": "High", "fat": "Medium"},
                "common_allergens": ["chicken"],
            },
            {
                "name": "Salmon",
                "description": "Rich in Omega-3 fatty acids.",
                "nutritional_value": {"protein": "High", "fat": "High"},
                "common_allergens": ["fish"],
            },
            {
                "name": "Brown Rice",
                "description": "Whole grain carbohydrate source.",
                "nutritional_value": {"fiber": "High", "carbs": "High"},
                "common_allergens": ["grain"],
            },
            {
                "name": "Taurine",
                "description": "Essential amino acid for cats.",
                "nutritional_value": {},
                "common_allergens": [],
            },
            {
                "name": "Sweet Potato",
                "description": "Digestible carbohydrate and fiber.",
                "nutritional_value": {"fiber": "Medium", "vitamins": ["A", "C"]},
                "common_allergens": [],
            },
        ]

        ingredients = {}
        for data in ingredients_data:
            ing = Ingredient(**data)
            session.add(ing)
            ingredients[data["name"]] = ing

        await session.commit()
        # Refresh to get IDs
        for ing in ingredients.values():
            await session.refresh(ing)

        print("Seeding products...")
        products_data = [
            {
                "name": "Premium Chicken Feast",
                "brand": "PurrfectChoice",
                "price": 25.99,
                "age_group": "adult",
                "food_type": "dry",
                "description": "A balanced diet for adult cats featuring real chicken.",
                "full_ingredient_list": "Chicken, Brown Rice, Sweet Potato, Taurine",
                "ingredient_names": ["Chicken", "Brown Rice", "Sweet Potato", "Taurine"],
            },
            {
                "name": "Salmon Delight",
                "brand": "OceanMeow",
                "price": 28.50,
                "age_group": "all_stages",
                "food_type": "wet",
                "description": "Succulent salmon chunks in gravy.",
                "full_ingredient_list": "Salmon, Taurine, Water",
                "ingredient_names": ["Salmon", "Taurine"],
            },
            {
                "name": "Kitten Growth Formula",
                "brand": "TinyPaws",
                "price": 30.00,
                "age_group": "kitten",
                "food_type": "dry",
                "description": "High protein formula for growing kittens.",
                "full_ingredient_list": "Chicken, Salmon, Brown Rice, Taurine",
                "ingredient_names": ["Chicken", "Salmon", "Brown Rice", "Taurine"],
            },
        ]

        products = []
        for data in products_data:
            ing_names = data.pop("ingredient_names")
            product = CatFoodProduct(**data)

            # Associate ingredients
            for name in ing_names:
                if name in ingredients:
                    product.ingredients.append(ingredients[name])

            session.add(product)
            products.append(product)

        await session.commit()
        for p in products:
            await session.refresh(p)

        print("Generating embeddings and indexing in Qdrant...")

        # Initialize Qdrant client
        client = qdrant_client.QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

        vector_store = QdrantVectorStore(client=client, collection_name="cat_food_products")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        documents = []
        for p in products:
            # Create a document for each product
            # We combine name, description and ingredients for the embedding text
            text = f"Product: {p.name}\nBrand: {p.brand}\nDescription: {p.description}\nIngredients: {p.full_ingredient_list}"

            doc = Document(
                text=text,
                metadata={
                    "product_id": p.id,
                    "name": p.name,
                    "brand": p.brand,
                    "age_group": p.age_group,
                    "food_type": p.food_type,
                },
            )
            documents.append(doc)

        # Create index (this will generate embeddings and store in Qdrant)
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

        # Update products with embedding IDs if needed (LlamaIndex manages IDs internally usually,
        # but if we wanted to link them explicitly we could.
        # For now, we just rely on metadata 'product_id').

        print("Seed data generation complete!")


if __name__ == "__main__":
    asyncio.run(seed_data())
