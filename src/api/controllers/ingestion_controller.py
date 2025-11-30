from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.domain.services.product_service import ProductService
from src.domain.services.ingredient_service import IngredientService
from src.domain.services.ingestion_service import IngestionService
from src.domain.repositories.product_repository import ProductRepository
from src.domain.repositories.ingredient_repository import IngredientRepository

router = APIRouter()

def get_ingestion_service(db: AsyncSession = Depends(get_db)) -> IngestionService:
    product_repo = ProductRepository(db)
    ingredient_repo = IngredientRepository(db)
    product_service = ProductService(product_repo)
    ingredient_service = IngredientService(ingredient_repo)
    return IngestionService(product_service, ingredient_service)

@router.post("/ingest/csv")
async def ingest_csv(
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    
    return await ingestion_service.ingest_csv_content(decoded_content)

