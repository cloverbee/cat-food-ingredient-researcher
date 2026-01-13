from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.rate_limit import limiter
from src.domain.repositories.ingredient_repository import IngredientRepository
from src.domain.repositories.product_repository import ProductRepository
from src.domain.services.ingestion_service import IngestionService
from src.domain.services.ingredient_service import IngredientService
from src.domain.services.product_service import ProductService

router = APIRouter()


def get_ingestion_service(db: AsyncSession = Depends(get_db)) -> IngestionService:
    product_repo = ProductRepository(db)
    ingredient_repo = IngredientRepository(db)
    product_service = ProductService(product_repo)
    ingredient_service = IngredientService(ingredient_repo)
    return IngestionService(product_service, ingredient_service)


@router.post("/ingest/csv")
@limiter.limit(f"{settings.RATE_LIMIT_ADMIN_PER_MINUTE}/minute", key_func=get_remote_address)
async def ingest_csv(
    request: Request,
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode("utf-8")

    return await ingestion_service.ingest_csv_content(decoded_content)
