"""
Delete cat food products from the database by matching product name.

This script deletes products whose name contains "Dry Dog Food" (case-insensitive).

Safe defaults:
- Always prints a preview (count + sample rows)
- Refuses to delete unless --yes is provided

Examples:
  # Preview products whose name contains "Dry Dog Food"
  python -m src.scripts.delete_products_by_name --contains "Dry Dog Food"

  # Delete products whose name contains "Dry Dog Food"
  python -m src.scripts.delete_products_by_name --contains "Dry Dog Food" --yes
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Iterable, List, Optional, Sequence

from sqlalchemy import delete, func, select, text

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct, product_ingredient_association


def _parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Delete cat food products by matching product name.")
    p.add_argument(
        "--contains",
        type=str,
        required=True,
        help="Substring to match in product name (case-insensitive).",
    )
    p.add_argument(
        "--sample",
        type=int,
        default=20,
        help="How many matching rows to print as a preview (default: 20).",
    )
    p.add_argument(
        "--delete-orphan-ingredients",
        action="store_true",
        help="Also delete ingredients that are no longer referenced by any product after deletion.",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Actually perform deletion. Without this flag, the command only prints a preview.",
    )
    return p.parse_args(list(argv) if argv is not None else None)


async def _fetch_matching_ids(where_clause) -> List[int]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CatFoodProduct.id).where(where_clause))
        return [row[0] for row in result.all()]


async def _preview(where_clause, *, sample: int) -> int:
    async with AsyncSessionLocal() as session:
        count_result = await session.execute(select(func.count()).select_from(CatFoodProduct).where(where_clause))
        total = int(count_result.scalar() or 0)

        if total == 0:
            print("Matched 0 products.")
            return 0

        print(f"Matched {total} products. Showing up to {sample} sample rows:\n")
        sample_stmt = (
            select(
                CatFoodProduct.id,
                CatFoodProduct.brand,
                CatFoodProduct.name,
            )
            .where(where_clause)
            .order_by(CatFoodProduct.id.asc())
            .limit(sample)
        )
        rows = (await session.execute(sample_stmt)).all()
        for r in rows:
            print(f"- id={r.id} brand={r.brand!r} name={r.name!r}")
        print("")
        return total


async def _delete_by_ids(
    ids: Sequence[int],
    *,
    delete_orphan_ingredients: bool,
) -> None:
    if not ids:
        print("Nothing to delete.")
        return

    async with AsyncSessionLocal() as session:
        # Order matters due to FK constraints - delete associations first
        await session.execute(
            delete(product_ingredient_association).where(product_ingredient_association.c.product_id.in_(list(ids)))
        )
        await session.execute(delete(CatFoodProduct).where(CatFoodProduct.id.in_(list(ids))))

        if delete_orphan_ingredients:
            # Remove any ingredients with no remaining associations.
            await session.execute(
                text(
                    """
                    DELETE FROM ingredient i
                    WHERE NOT EXISTS (
                      SELECT 1
                      FROM product_ingredient_association pia
                      WHERE pia.ingredient_id = i.id
                    )
                    """
                )
            )

        await session.commit()


async def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _parse_args(argv)

    # Build case-insensitive filter for product name
    needle = (args.contains or "").strip().lower()
    if not needle:
        print("Error: --contains cannot be empty.")
        return 2

    like_val = f"%{needle}%"
    where_clause = func.lower(CatFoodProduct.name).like(like_val)

    await _preview(where_clause, sample=args.sample)

    if not args.yes:
        print("Refusing to delete without --yes. Re-run with --yes to apply.")
        return 2

    ids = await _fetch_matching_ids(where_clause)
    await _delete_by_ids(ids, delete_orphan_ingredients=args.delete_orphan_ingredients)
    print(f"✅ Deleted {len(ids)} products.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
