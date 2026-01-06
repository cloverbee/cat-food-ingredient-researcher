"""
Update product descriptions and ingredients from an Excel file.

This script reads an Excel file with product names, descriptions, and ingredients,
finds matching products in the database by name, and updates their description
and full_ingredient_list fields.

Usage:
  python -m src.scripts.update_products_from_excel --excel "cat food data.xlsx"
"""

import argparse
import asyncio
from pathlib import Path

import pandas as pd
from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct


async def update_products_from_excel(excel_path: Path) -> dict:
    """
    Read Excel file and update matching products in the database.

    Expected Excel columns:
    - name: Product name to match against database
    - description: Product description to update
    - ingredient (or similar): Ingredients column (will be comma-separated)
    """
    # Read Excel file
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)

    print(f"Found {len(df)} rows in Excel file")
    print(f"Columns: {df.columns.tolist()}")

    # Find columns (case-insensitive, flexible matching)
    name_col = None
    description_col = None
    ingredient_col = None

    for col in df.columns:
        col_lower = col.lower().strip()
        if "name" in col_lower and name_col is None:
            name_col = col
        # Check for description or details column
        if ("description" in col_lower or "details" in col_lower) and description_col is None:
            description_col = col
        if "ingredient" in col_lower and ingredient_col is None:
            ingredient_col = col

    if name_col is None:
        raise ValueError(f"Could not find a 'name' column in the Excel file. Available columns: {df.columns.tolist()}")

    if description_col is None:
        print(f"Warning: Could not find a 'description' column. Available columns: {df.columns.tolist()}")
        print("Description updates will be skipped.")

    if ingredient_col is None:
        raise ValueError(
            f"Could not find an 'ingredient' column in the Excel file. Available columns: {df.columns.tolist()}"
        )

    print("Using columns:")
    print(f"  Name: {name_col}")
    if description_col:
        print(f"  Description: {description_col}")
    print(f"  Ingredient: {ingredient_col}")

    updated_count = 0
    not_found = []

    async with AsyncSessionLocal() as db:
        for idx, row in df.iterrows():
            product_name = str(row[name_col]).strip()
            description = row[description_col] if description_col and pd.notna(row[description_col]) else None
            ingredients_raw = row[ingredient_col] if pd.notna(row[ingredient_col]) else None

            if not product_name:
                print(f"Row {idx + 1}: Skipping empty product name")
                continue

            # Find product by name (case-insensitive, partial match)
            stmt = select(CatFoodProduct).where(CatFoodProduct.name.ilike(f"%{product_name}%"))
            result = await db.execute(stmt)
            products = result.scalars().all()

            if not products:
                not_found.append(product_name)
                print(f"Row {idx + 1}: Product '{product_name}' not found in database")
                continue

            # If multiple matches, try exact match first
            exact_match = None
            for p in products:
                if p.name.lower() == product_name.lower():
                    exact_match = p
                    break

            product = exact_match if exact_match else products[0]

            if len(products) > 1 and not exact_match:
                print(f"Row {idx + 1}: Multiple matches for '{product_name}', updating first match: '{product.name}'")

            # Process ingredients - separate by comma if needed
            ingredients_text = None
            if ingredients_raw:
                ingredients_str = str(ingredients_raw).strip()
                # If ingredients are already comma-separated, use as-is
                # Otherwise, try to split by common separators
                if "," in ingredients_str:
                    # Already comma-separated, just clean up
                    ingredients_text = ", ".join([i.strip() for i in ingredients_str.split(",")])
                elif ";" in ingredients_str:
                    # Semicolon-separated, convert to comma
                    ingredients_text = ", ".join([i.strip() for i in ingredients_str.split(";")])
                elif "\n" in ingredients_str:
                    # Newline-separated, convert to comma
                    ingredients_text = ", ".join([i.strip() for i in ingredients_str.split("\n") if i.strip()])
                else:
                    # Single ingredient or space-separated, use as-is
                    ingredients_text = ingredients_str

            # Update product
            if description:
                product.description = description
            if ingredients_text:
                product.full_ingredient_list = ingredients_text

            updated_count += 1
            print(f"Row {idx + 1}: Updated '{product.name}' (ID: {product.id})")

        # Commit all changes
        await db.commit()

    return {"updated": updated_count, "not_found": not_found, "total_rows": len(df)}


async def _main_async() -> None:
    parser = argparse.ArgumentParser(description="Update cat food products from Excel file")
    parser.add_argument("--excel", required=True, help="Path to Excel file with product data")
    args = parser.parse_args()

    excel_path = Path(args.excel).expanduser().resolve()
    if not excel_path.exists():
        raise SystemExit(f"Excel file not found: {excel_path}")

    result = await update_products_from_excel(excel_path)

    print("\n" + "=" * 50)
    print("Update Summary:")
    print(f"  Total rows processed: {result['total_rows']}")
    print(f"  Products updated: {result['updated']}")
    print(f"  Products not found: {len(result['not_found'])}")

    if result["not_found"]:
        print("\nProducts not found in database:")
        for name in result["not_found"]:
            print(f"  - {name}")
    print("=" * 50)


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
