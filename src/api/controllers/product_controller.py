from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.rate_limit import limiter
from src.domain.repositories.product_repository import ProductRepository
from src.domain.schemas.product import ProductCreate, ProductRead
from src.domain.services.product_service import ProductService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    repository = ProductRepository(db)
    return ProductService(repository)


@router.post("/", response_model=ProductRead)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute", key_func=get_remote_address)
async def create_product(
    request: Request,
    product: ProductCreate,
    service: ProductService = Depends(get_service),
):
    return await service.create_product(product)


@router.get("/", response_model=List[ProductRead])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute", key_func=get_remote_address)
async def read_products(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_service),
):
    return await service.get_products(skip, limit)


@router.get("/{product_id}", response_model=ProductRead)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute", key_func=get_remote_address)
async def read_product(
    request: Request,
    product_id: int,
    service: ProductService = Depends(get_service),
):
    product = await service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute", key_func=get_remote_address)
async def delete_product(
    request: Request,
    product_id: int,
    service: ProductService = Depends(get_service),
):
    deleted = await service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}
