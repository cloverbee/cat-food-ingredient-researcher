"""
Import products from a CSV into the database.

This reuses the same backend ingestion logic (IngestionService) that powers:
  POST /api/v1/admin/ingest/csv

Usage:
  python -m src.scripts.import_products_csv_to_db --csv path/to/products.csv
"""

import argparse
import asyncio
from pathlib import Path

from src.core.database import AsyncSessionLocal
from src.domain.repositories.ingredient_repository import IngredientRepository
from src.domain.repositories.product_repository import ProductRepository
from src.domain.services.ingestion_service import IngestionService
from src.domain.services.ingredient_service import IngredientService
from src.domain.services.product_service import ProductService


def _build_ingestion_service(db_session) -> IngestionService:
    product_repo = ProductRepository(db_session)
    ingredient_repo = IngredientRepository(db_session)
    product_service = ProductService(product_repo)
    ingredient_service = IngredientService(ingredient_repo)
    return IngestionService(product_service, ingredient_service)


async def import_csv_file(csv_path: Path) -> dict:
    csv_text = csv_path.read_text(encoding="utf-8")
    async with AsyncSessionLocal() as db:
        ingestion_service = _build_ingestion_service(db)
        return await ingestion_service.ingest_csv_content(csv_text)


async def _main_async() -> None:
    parser = argparse.ArgumentParser(description="Import cat food products CSV into the database")
    parser.add_argument("--csv", required=True, help="Path to ingestion-format CSV file")
    args = parser.parse_args()

    csv_path = Path(args.csv).expanduser().resolve()
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    result = await import_csv_file(csv_path)
    print(result.get("message", result))


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
