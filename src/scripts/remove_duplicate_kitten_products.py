"""
Remove duplicate kitten cat food products from the database.

For each group of kitten products with the same normalized name:
- Keeps the entry with the most complete data (description, image_url, shopping_url)
- Deletes duplicates

Safe defaults:
- Always prints a preview (count + sample rows)
- Refuses to delete unless --yes is provided

Usage:
  # Preview duplicates that would be removed
  python -m src.scripts.remove_duplicate_kitten_products

  # Actually remove duplicates
  python -m src.scripts.remove_duplicate_kitten_products --yes
"""

from __future__ import annotations

import argparse
import asyncio
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from sqlalchemy import delete, func, select

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct, product_ingredient_association

_SIZE_RE = re.compile(
    r"\b(\d+(\.\d+)?)\s*(lb|lbs|pound|pounds|oz|ounce|ounces|kg|g|ct|count)\b",
    re.IGNORECASE,
)


def _normalize_name_for_dedupe(name: str) -> str:
    """Normalize product name for duplicate detection."""
    n = name.lower()
    n = re.sub(r"[^\w\s]", " ", n)
    n = _SIZE_RE.sub(" ", n)
    n = re.sub(r"\b(dry|wet|canned|kibble|cat|food|foods)\b", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def _normalize_brand_for_dedupe(brand: str) -> str:
    """Normalize brand name for duplicate detection."""
    b = brand.lower()
    b = re.sub(r"[^\w\s]", " ", b)
    b = re.sub(r"\s+", " ", b).strip()
    return b


def _score_product(product: CatFoodProduct) -> int:
    """
    Score a product based on data completeness.
    Higher score = more complete data.
    """
    score = 0
    if product.description and product.description.strip():
        score += 2
    if product.image_url and product.image_url.strip():
        score += 1
    if product.shopping_url and product.shopping_url.strip():
        score += 1
    if product.full_ingredient_list and product.full_ingredient_list.strip():
        score += 1
    if product.price is not None:
        score += 1
    return score


async def find_kitten_duplicate_groups() -> Dict[str, List[CatFoodProduct]]:
    """
    Find all kitten products grouped by normalized name.
    Returns a dict mapping normalized name to list of products.
    """
    async with AsyncSessionLocal() as db:
        # Filter for kitten products (case-insensitive)
        result = await db.execute(
            select(CatFoodProduct)
            .where(func.lower(CatFoodProduct.age_group).like("%kitten%"))
            .order_by(CatFoodProduct.name, CatFoodProduct.id)
        )
        all_products = result.scalars().all()

    # Group by normalized name (lowercase, cleaned)
    groups: Dict[str, List[CatFoodProduct]] = defaultdict(list)
    for product in all_products:
        normalized_name = _normalize_name_for_dedupe(product.name)
        groups[normalized_name].append(product)

    # Filter to only groups with duplicates (more than 1 product)
    duplicate_groups = {name: products for name, products in groups.items() if len(products) > 1}

    return duplicate_groups


def identify_products_to_delete(products: List[CatFoodProduct]) -> Tuple[List[CatFoodProduct], List[CatFoodProduct]]:
    """
    For a group of products with the same normalized name, identify which to keep and which to delete.

    Strategy:
    - Score each product by data completeness
    - Keep the product with the highest score (or lowest ID if tied)
    - Delete all others

    Returns:
        (products_to_keep, products_to_delete)
    """
    if not products:
        return ([], [])

    # Score all products
    scored_products = [(p, _score_product(p)) for p in products]

    # Sort by score (descending), then by ID (ascending) for tie-breaking
    scored_products.sort(key=lambda x: (-x[1], x[0].id))

    product_to_keep = scored_products[0][0]
    products_to_delete = [p for p, _ in scored_products[1:]]

    return ([product_to_keep], products_to_delete)


async def preview_duplicates() -> Dict[str, Tuple[List[CatFoodProduct], List[CatFoodProduct]]]:
    """
    Preview duplicate kitten products and what would be deleted.
    Returns a dict mapping normalized name to (keep_list, delete_list).
    """
    duplicate_groups = await find_kitten_duplicate_groups()

    if not duplicate_groups:
        print("✅ No duplicate kitten products found (by normalized name).")
        return {}

    print(f"Found {len(duplicate_groups)} duplicate kitten product group(s):\n")

    decisions: Dict[str, Tuple[List[CatFoodProduct], List[CatFoodProduct]]] = {}
    total_to_delete = 0

    for normalized_name, products in sorted(duplicate_groups.items()):
        to_keep, to_delete = identify_products_to_delete(products)
        decisions[normalized_name] = (to_keep, to_delete)
        total_to_delete += len(to_delete)

        print(f"Name: '{products[0].name}' ({len(products)} duplicates)")
        print(f"  Will KEEP ({len(to_keep)}):")
        for product in to_keep:
            score = _score_product(product)
            desc_preview = (
                (product.description[:50] + "...")
                if product.description and len(product.description) > 50
                else (product.description or "(no description)")
            )
            print(
                f"    - ID {product.id}: {product.brand} | {product.name} | Score: {score} | Description: {desc_preview}"
            )

        if to_delete:
            print(f"  Will DELETE ({len(to_delete)}):")
            for product in to_delete:
                score = _score_product(product)
                print(f"    - ID {product.id}: {product.brand} | {product.name} | Score: {score}")
        print()

    print(f"Total kitten products to delete: {total_to_delete}")
    return decisions


async def delete_duplicates(decisions: Dict[str, Tuple[List[CatFoodProduct], List[CatFoodProduct]]]) -> int:
    """
    Delete the duplicate kitten products identified in the decisions dict.
    Returns the number of products deleted.
    """
    # Collect all IDs to delete
    ids_to_delete = []
    for _to_keep, to_delete in decisions.values():
        ids_to_delete.extend([p.id for p in to_delete])

    if not ids_to_delete:
        print("No products to delete.")
        return 0

    async with AsyncSessionLocal() as db:
        # Delete associations first (due to FK constraints)
        await db.execute(
            delete(product_ingredient_association).where(product_ingredient_association.c.product_id.in_(ids_to_delete))
        )

        # Delete products
        await db.execute(delete(CatFoodProduct).where(CatFoodProduct.id.in_(ids_to_delete)))

        await db.commit()

    return len(ids_to_delete)


def _parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Remove duplicate kitten cat food products")
    p.add_argument(
        "--yes",
        action="store_true",
        help="Actually perform deletion. Without this flag, the command only prints a preview.",
    )
    return p.parse_args(list(argv) if argv is not None else None)


async def main(argv: Optional[list] = None) -> int:
    args = _parse_args(argv)

    print("=" * 60)
    print("Remove Duplicate Kitten Products")
    print("=" * 60)
    print()

    # Preview duplicates
    decisions = await preview_duplicates()

    if not decisions:
        return 0

    if not args.yes:
        print("\n⚠️  Refusing to delete without --yes. Re-run with --yes to apply.")
        return 2

    # Confirm deletion
    total_to_delete = sum(len(to_delete) for to_keep, to_delete in decisions.values())
    print(f"\n🗑️  Deleting {total_to_delete} duplicate kitten product(s)...")

    deleted_count = await delete_duplicates(decisions)

    print(f"\n✅ Successfully deleted {deleted_count} duplicate kitten product(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
