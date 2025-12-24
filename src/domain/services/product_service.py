from typing import List, Optional

from src.domain.repositories.product_repository import ProductRepository
from src.domain.schemas.product import ProductCreate, ProductRead


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def create_product(self, product: ProductCreate) -> ProductRead:
        return await self.repository.create(product)

    async def get_product(self, product_id: int) -> Optional[ProductRead]:
        return await self.repository.get(product_id)

    async def get_products(self, skip: int = 0, limit: int = 100) -> List[ProductRead]:
        return await self.repository.get_all(skip, limit)

    async def delete_product(self, product_id: int) -> bool:
        return await self.repository.delete(product_id)
