"""
Restore image URLs and shopping URLs from CSV file.

This script matches products in the database by name with products in a CSV file
and updates their image_url and shopping_url fields.

Usage:
  python -m src.scripts.restore_images_from_csv --csv cat_food_popular_merged.csv
"""

import argparse
import asyncio
import csv
from pathlib import Path
from typing import Dict, Optional

from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct


def normalize_name(name: str) -> str:
    """Normalize product name for matching."""
    if not name:
        return ""
    # Remove extra whitespace, convert to lowercase
    return " ".join(name.lower().split())


def find_best_match(product_name: str, csv_products: Dict[str, Dict]) -> Optional[Dict]:
    """Find the best matching product from CSV by name."""
    normalized_target = normalize_name(product_name)

    # Try exact match first
    if normalized_target in csv_products:
        return csv_products[normalized_target]

    # Try partial matches
    best_match = None
    best_score = 0

    for csv_name, csv_data in csv_products.items():
        # Check if target name contains CSV name or vice versa
        if normalized_target in csv_name or csv_name in normalized_target:
            # Score based on length of match
            match_length = min(len(normalized_target), len(csv_name))
            if match_length > best_score:
                best_score = match_length
                best_match = csv_data

    return best_match


async def restore_images_from_csv(csv_path: Path) -> dict:
    """Restore image URLs and shopping URLs from CSV file."""
    print(f"Reading CSV file: {csv_path}")

    # Read CSV file
    csv_products = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            if name:
                normalized = normalize_name(name)
                csv_products[normalized] = {
                    "name": name,
                    "image_url": row.get("image_url", "").strip() or None,
                    "shopping_url": row.get("shopping_url", "").strip() or None,
                }

    print(f"Found {len(csv_products)} products in CSV file")

    # Update database products
    updated_count = 0
    not_found_count = 0
    already_has_images = 0

    async with AsyncSessionLocal() as db:
        # Get all products from database
        result = await db.execute(select(CatFoodProduct))
        db_products = result.scalars().all()

        print(f"Found {len(db_products)} products in database")
        print("\nMatching and updating products...")

        for db_product in db_products:
            match = find_best_match(db_product.name, csv_products)

            if not match:
                not_found_count += 1
                print(f"  ⚠️  No match found for: {db_product.name}")
                continue

            # Check if product already has images
            has_image = db_product.image_url is not None and db_product.image_url.strip() != ""
            has_shopping = db_product.shopping_url is not None and db_product.shopping_url.strip() != ""

            if has_image and has_shopping:
                already_has_images += 1
                continue

            # Update image URL if missing and CSV has it
            if match.get("image_url") and not has_image:
                db_product.image_url = match["image_url"]
                print(f"  ✅ Updated image for: {db_product.name}")

            # Update shopping URL if missing and CSV has it
            if match.get("shopping_url") and not has_shopping:
                db_product.shopping_url = match["shopping_url"]
                print(f"  ✅ Updated shopping URL for: {db_product.name}")

            if (match.get("image_url") and not has_image) or (match.get("shopping_url") and not has_shopping):
                updated_count += 1

        # Commit all changes
        await db.commit()

    return {
        "updated": updated_count,
        "not_found": not_found_count,
        "already_has_images": already_has_images,
        "total_db_products": len(db_products),
        "total_csv_products": len(csv_products),
    }


async def main_async():
    """Main async function."""
    parser = argparse.ArgumentParser(description="Restore image URLs and shopping URLs from CSV file")
    parser.add_argument("--csv", required=True, help="Path to CSV file with image_url and shopping_url columns")
    args = parser.parse_args()

    csv_path = Path(args.csv).expanduser().resolve()
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    print("=" * 70)
    print("Restore Images and Shopping URLs from CSV")
    print("=" * 70)

    result = await restore_images_from_csv(csv_path)

    print("\n" + "=" * 70)
    print("Restore Summary:")
    print(f"  Total products in database: {result['total_db_products']}")
    print(f"  Total products in CSV: {result['total_csv_products']}")
    print(f"  Products updated: {result['updated']}")
    print(f"  Products already had images/URLs: {result['already_has_images']}")
    print(f"  Products not found in CSV: {result['not_found']}")
    print("=" * 70)


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
