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
            # Create Product
            product_data = ProductCreate(
                name=row.get('name'),
                brand=row.get('brand'),
                price=float(row.get('price', 0)),
                age_group=row.get('age_group'),
                food_type=row.get('food_type'),
                description=row.get('description'),
                full_ingredient_list=row.get('full_ingredient_list')
            )
            
            # Note: Parsing ingredients from full_ingredient_list and creating Ingredient objects 
            # is complex and depends on the format. For now, we just store the product.
            # A more advanced implementation would parse the string and link/create ingredients.
            
            await product_service.create_product(product_data)
            products_created += 1
            
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            continue

    return {"message": f"Successfully ingested {products_created} products."}
