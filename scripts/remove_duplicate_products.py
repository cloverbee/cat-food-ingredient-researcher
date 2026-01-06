#!/usr/bin/env python3
"""
Remove duplicate cat food products with identical names.

For each group of products with the same name (case-insensitive):
- Keeps the entry with non-empty description
- Deletes the entry where description is null/empty

Safe defaults:
- Always prints a preview (count + sample rows)
- Refuses to delete unless --yes is provided

Usage:
  # Preview duplicates that would be removed
  python3 scripts/remove_duplicate_products.py

  # Actually remove duplicates
  python3 scripts/remove_duplicate_products.py --yes
"""

import asyncio
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from sqlalchemy import delete, select

# Add project root to path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct, product_ingredient_association


async def find_duplicate_groups() -> Dict[str, List[CatFoodProduct]]:
    """
    Find all products grouped by name (case-insensitive).
    Returns a dict mapping normalized name to list of products.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(CatFoodProduct).order_by(CatFoodProduct.name, CatFoodProduct.id))
        all_products = result.scalars().all()

    # Group by normalized name (lowercase)
    groups: Dict[str, List[CatFoodProduct]] = defaultdict(list)
    for product in all_products:
        normalized_name = product.name.lower().strip()
        groups[normalized_name].append(product)

    # Filter to only groups with duplicates (more than 1 product)
    duplicate_groups = {name: products for name, products in groups.items() if len(products) > 1}

    return duplicate_groups


def identify_products_to_delete(products: List[CatFoodProduct]) -> Tuple[List[CatFoodProduct], List[CatFoodProduct]]:
    """
    For a group of products with the same name, identify which to keep and which to delete.

    Strategy:
    - If any product has a non-empty description, keep the first one with description (by ID)
    - Otherwise, keep the first product overall (by ID)
    - Delete all others

    Returns:
        (products_to_keep, products_to_delete)
    """
    # Separate products by whether they have description
    with_description = []
    without_description = []

    for product in products:
        # Check if description is non-empty
        if product.description and product.description.strip():
            with_description.append(product)
        else:
            without_description.append(product)

    # If we have products with description, keep the first one (by ID) and delete all others
    if with_description:
        # Sort by ID to get a deterministic choice
        sorted_with_desc = sorted(with_description, key=lambda p: p.id)
        product_to_keep = sorted_with_desc[0]
        products_to_delete = sorted_with_desc[1:] + without_description
        return ([product_to_keep], products_to_delete)

    # If all have empty descriptions, keep the first one (by ID) and delete the rest
    if without_description:
        sorted_products = sorted(without_description, key=lambda p: p.id)
        return ([sorted_products[0]], sorted_products[1:])

    # Shouldn't happen, but handle edge case
    return (products[:1], products[1:])


async def preview_duplicates() -> Dict[str, Tuple[List[CatFoodProduct], List[CatFoodProduct]]]:
    """
    Preview duplicate products and what would be deleted.
    Returns a dict mapping normalized name to (keep_list, delete_list).
    """
    duplicate_groups = await find_duplicate_groups()

    if not duplicate_groups:
        print("✅ No duplicate products found (by name).")
        return {}

    print(f"Found {len(duplicate_groups)} duplicate name group(s):\n")

    decisions: Dict[str, Tuple[List[CatFoodProduct], List[CatFoodProduct]]] = {}
    total_to_delete = 0

    for normalized_name, products in sorted(duplicate_groups.items()):
        to_keep, to_delete = identify_products_to_delete(products)
        decisions[normalized_name] = (to_keep, to_delete)
        total_to_delete += len(to_delete)

        print(f"Name: '{products[0].name}' ({len(products)} duplicates)")
        print(f"  Will KEEP ({len(to_keep)}):")
        for product in to_keep:
            desc_preview = (
                (product.description[:50] + "...")
                if product.description and len(product.description) > 50
                else (product.description or "(no description)")
            )
            print(f"    - ID {product.id}: {product.name} | Description: {desc_preview}")

        if to_delete:
            print(f"  Will DELETE ({len(to_delete)}):")
            for product in to_delete:
                print(
                    f"    - ID {product.id}: {product.name} | Description: {'(empty/null)' if not product.description or not product.description.strip() else product.description[:50] + '...'}"
                )
        print()

    print(f"Total products to delete: {total_to_delete}")
    return decisions


async def delete_duplicates(decisions: Dict[str, Tuple[List[CatFoodProduct], List[CatFoodProduct]]]) -> int:
    """
    Delete the duplicate products identified in the decisions dict.
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


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Remove duplicate cat food products with identical names")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Actually perform deletion. Without this flag, the command only prints a preview.",
    )
    args = parser.parse_args()

    # Preview duplicates
    decisions = await preview_duplicates()

    if not decisions:
        return

    if not args.yes:
        print("\n⚠️  Refusing to delete without --yes. Re-run with --yes to apply.")
        return

    # Confirm deletion
    total_to_delete = sum(len(to_delete) for to_keep, to_delete in decisions.values())
    print(f"\n🗑️  Deleting {total_to_delete} duplicate product(s)...")

    deleted_count = await delete_duplicates(decisions)

    print(f"\n✅ Successfully deleted {deleted_count} duplicate product(s).")


if __name__ == "__main__":
    asyncio.run(main())
