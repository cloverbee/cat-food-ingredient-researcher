"""
Delete cat food products from the database that have no image URL.

This script identifies products where image_url is NULL or empty and removes them.

Safe defaults:
- Always prints a preview (count + sample rows)
- Refuses to delete unless --yes is provided

Examples:
  # Preview products without images
  python -m src.scripts.delete_products_without_image

  # Delete products without images
  python -m src.scripts.delete_products_without_image --yes
"""

from __future__ import annotations

import argparse
import asyncio
from typing import List, Optional, Sequence

from sqlalchemy import delete, func, or_, select, text

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct, product_ingredient_association


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Delete cat food products that have no image URL.")
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


async def _fetch_matching_ids() -> List[int]:
    """Find all product IDs where image_url is NULL or empty."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CatFoodProduct.id).where(
                or_(
                    CatFoodProduct.image_url.is_(None),
                    CatFoodProduct.image_url == "",
                )
            )
        )
        return [row[0] for row in result.all()]


async def _preview(*, sample: int) -> int:
    """Print a preview of products that will be deleted."""
    async with AsyncSessionLocal() as session:
        count_result = await session.execute(
            select(func.count())
            .select_from(CatFoodProduct)
            .where(
                or_(
                    CatFoodProduct.image_url.is_(None),
                    CatFoodProduct.image_url == "",
                )
            )
        )
        total = int(count_result.scalar() or 0)

        if total == 0:
            print("✅ No products found without images.")
            return 0

        print(f"Found {total} product(s) without images. Showing up to {sample} sample rows:\n")
        sample_stmt = (
            select(
                CatFoodProduct.id,
                CatFoodProduct.brand,
                CatFoodProduct.name,
                CatFoodProduct.food_type,
                CatFoodProduct.shopping_url,
            )
            .where(
                or_(
                    CatFoodProduct.image_url.is_(None),
                    CatFoodProduct.image_url == "",
                )
            )
            .order_by(CatFoodProduct.id.asc())
            .limit(sample)
        )
        rows = (await session.execute(sample_stmt)).all()
        for r in rows:
            print(f"- id={r.id} brand={r.brand!r} name={r.name!r} type={r.food_type}")
            if r.shopping_url:
                print(f"  shopping_url={r.shopping_url[:80]!r}...")
        print("")
        return total


async def _delete_by_ids(
    ids: Sequence[int],
    *,
    delete_orphan_ingredients: bool,
) -> None:
    """Delete products by their IDs."""
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
            # Remove any ingredients with no remaining associations
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


async def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)

    total = await _preview(sample=args.sample)

    if total == 0:
        return 0

    if not args.yes:
        print("⚠️  Refusing to delete without --yes. Re-run with --yes to apply.")
        return 2

    ids = await _fetch_matching_ids()
    await _delete_by_ids(ids, delete_orphan_ingredients=args.delete_orphan_ingredients)
    print(f"✅ Deleted {len(ids)} product(s) without images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
