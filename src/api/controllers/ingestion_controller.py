from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io
from typing import List

from src.core.database import get_db
from src.domain.services.product_service import ProductService
from src.domain.services.ingredient_service import IngredientService
from src.domain.repositories.product_repository import ProductRepository
from src.domain.repositories.ingredient_repository import IngredientRepository
from src.domain.schemas.product import ProductCreate
from src.domain.schemas.ingredient import IngredientCreate

router = APIRouter()

def get_services(db: AsyncSession = Depends(get_db)):
    product_repo = ProductRepository(db)
    ingredient_repo = IngredientRepository(db)
    return ProductService(product_repo), IngredientService(ingredient_repo)

@router.post("/ingest/csv")
async def ingest_csv(
    file: UploadFile = File(...),
    services: tuple[ProductService, IngredientService] = Depends(get_services)
):
    product_service, ingredient_service = services
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))

    products_created = 0
    
    for row in csv_reader:
        # Expected CSV columns: name, brand, price, age_group, food_type, description, full_ingredient_list
        try:
            # Parse ingredients if available
            ingredient_ids = []
            raw_ingredients = row.get('full_ingredient_list')
            if raw_ingredients:
                # Split by comma and strip whitespace
                ingredient_names = [name.strip() for name in raw_ingredients.split(',') if name.strip()]
                if ingredient_names:
                    ingredients = await ingredient_service.get_or_create_ingredients(ingredient_names)
                    ingredient_ids = [ing.id for ing in ingredients]

            # Create Product
            product_data = ProductCreate(
                name=row.get('name'),
                brand=row.get('brand'),
                price=float(row.get('price', 0)),
                age_group=row.get('age_group'),
                food_type=row.get('food_type'),
                description=row.get('description'),
                full_ingredient_list=raw_ingredients,
                ingredient_ids=ingredient_ids
            )
            
            await product_service.create_product(product_data)
            products_created += 1
            
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            continue

    return {"message": f"Successfully ingested {products_created} products."}
