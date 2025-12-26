"""
Reset (truncate) database tables and optionally import products from a CSV.

Why this exists:
- Dropping tables is risky with Alembic migrations.
- We want a repeatable, safe way to clear product/ingredient data and reload.

Default behavior:
- Truncates: product_ingredient_association, cat_food_product, ingredient
- Keeps: user table (unless --include-users is passed)

CSV format (header row):
name,brand,price,age_group,food_type,description,full_ingredient_list,image_url,shopping_url

Examples:
  # Wipe products+ingredients and import sample file
  python -m src.scripts.reset_and_import --yes --csv sample_products.csv

  # Wipe only (no import)
  python -m src.scripts.reset_and_import --yes --wipe-only
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import io
import re
from pathlib import Path
from typing import Dict, Iterable, Optional

from sqlalchemy import text

from src.core.database import AsyncSessionLocal
from src.domain.repositories.ingredient_repository import IngredientRepository
from src.domain.repositories.product_repository import ProductRepository
from src.domain.services.ingestion_service import IngestionService
from src.domain.services.ingredient_service import IngredientService
from src.domain.services.product_service import ProductService


def _clean_str(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None
    v = val.strip()
    if not v:
        return None
    # Collapse internal whitespace
    v = re.sub(r"\s+", " ", v)
    return v


def _normalize_csv_row(row: Dict[str, str]) -> Dict[str, str]:
    """
    Normalize incoming CSV rows:
    - trim whitespace
    - treat empty strings as missing
    - accept common header variants (case/space differences)
    """
    # Normalize header keys first
    key_map = {
        "name": "name",
        "product_name": "name",
        "brand": "brand",
        "price": "price",
        "age_group": "age_group",
        "age": "age_group",
        "food_type": "food_type",
        "foodtype": "food_type",
        "type": "food_type",
        "description": "description",
        "full_ingredient_list": "full_ingredient_list",
        "ingredients": "full_ingredient_list",
        "ingredient_list": "full_ingredient_list",
        "image_url": "image_url",
        "image": "image_url",
        "shopping_url": "shopping_url",
        "url": "shopping_url",
        "link": "shopping_url",
    }

    normalized: Dict[str, str] = {}
    for k, v in row.items():
        canon_key = re.sub(r"[\s\-]+", "_", (k or "").strip().lower())
        mapped = key_map.get(canon_key)
        if not mapped:
            continue
        cleaned = _clean_str(v)
        if cleaned is not None:
            normalized[mapped] = cleaned

    # Slightly normalize categorical fields for consistency
    if "food_type" in normalized:
        normalized["food_type"] = normalized["food_type"].lower()
    if "age_group" in normalized:
        normalized["age_group"] = normalized["age_group"].lower()

    return normalized


async def truncate_data(*, include_users: bool) -> None:
    """
    Truncate application data tables.

    We use TRUNCATE instead of drop_all so Alembic migrations remain valid.
    """
    async with AsyncSessionLocal() as session:
        tables = ["product_ingredient_association", "cat_food_product", "ingredient"]
        if include_users:
            # user is a reserved keyword in Postgres; must be quoted
            tables.append('"user"')

        sql = f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE;"
        await session.execute(text(sql))
        await session.commit()


async def import_csv(path: Path) -> Dict[str, int]:
    csv_text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(csv_text))

    async with AsyncSessionLocal() as session:
        product_repo = ProductRepository(session)
        ingredient_repo = IngredientRepository(session)
        product_service = ProductService(product_repo)
        ingredient_service = IngredientService(ingredient_repo)
        ingestion_service = IngestionService(product_service, ingredient_service)

        created = 0
        failed = 0
        for raw_row in reader:
            row = _normalize_csv_row(raw_row)
            try:
                await ingestion_service.ingest_product_from_row(row)
                created += 1
            except Exception:
                # Keep going; we want "best effort" imports for messy CSVs
                failed += 1

    return {"created": created, "failed": failed}


def _parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Truncate DB tables and import products from CSV.")
    p.add_argument(
        "--yes",
        action="store_true",
        help="Required confirmation flag (this will DELETE data).",
    )
    p.add_argument(
        "--csv",
        action="append",
        default=[],
        help="Path to a CSV file to import (can be provided multiple times).",
    )
    p.add_argument(
        "--wipe-only",
        action="store_true",
        help="Only truncate tables (no import).",
    )
    p.add_argument(
        "--include-users",
        action="store_true",
        help="Also truncate the user table (off by default).",
    )
    return p.parse_args(list(argv) if argv is not None else None)


async def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _parse_args(argv)

    if not args.yes:
        print("Refusing to run without --yes (this command deletes data).")
        return 2

    await truncate_data(include_users=args.include_users)
    print("✅ Truncated tables.")

    if args.wipe_only:
        return 0

    if not args.csv:
        print("No --csv provided. Use --wipe-only to only truncate.")
        return 2

    total_created = 0
    total_failed = 0
    for csv_path in args.csv:
        path = Path(csv_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"CSV not found: {path}")
        result = await import_csv(path)
        total_created += result["created"]
        total_failed += result["failed"]
        print(f"Imported {path.name}: created={result['created']} failed={result['failed']}")

    print(f"✅ Import done. created={total_created} failed={total_failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
