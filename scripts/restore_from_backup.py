#!/usr/bin/env python3
"""
Restore database from CSV backup files.

This script restores products, ingredients, and associations from backup CSV files.
It will clear existing data and restore from the backup.

Usage:
    python3 scripts/restore_from_backup.py --backup-dir backups/20260106_170116
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import settings
from src.domain.models.ingredient import Ingredient
from src.domain.models.product import CatFoodProduct, product_ingredient_association


async def restore_from_backup(backup_dir: Path):
    """Restore database from CSV backup files."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    backup_dir = Path(backup_dir).expanduser().resolve()

    if not backup_dir.exists():
        raise FileNotFoundError(f"Backup directory not found: {backup_dir}")

    products_csv = backup_dir / "cat_food_product.csv"
    ingredients_csv = backup_dir / "ingredient.csv"
    associations_csv = backup_dir / "product_ingredient_association.csv"

    if not products_csv.exists():
        raise FileNotFoundError(f"Products backup not found: {products_csv}")
    if not ingredients_csv.exists():
        raise FileNotFoundError(f"Ingredients backup not found: {ingredients_csv}")
    if not associations_csv.exists():
        raise FileNotFoundError(f"Associations backup not found: {associations_csv}")

    print("=" * 80)
    print("RESTORING DATABASE FROM BACKUP")
    print("=" * 80)
    print(f"Backup directory: {backup_dir}")
    print()

    try:
        async with async_session() as session:
            # Step 1: Clear existing data
            print("Clearing existing data...")
            await session.execute(delete(product_ingredient_association))
            await session.execute(delete(CatFoodProduct))
            await session.execute(delete(Ingredient))
            await session.commit()
            print("✓ Cleared existing data")
            print()

            # Step 2: Restore ingredients
            print("Restoring ingredients...")
            df_ingredients = pd.read_csv(ingredients_csv)
            ingredients_map = {}  # old_id -> new_id mapping

            for _, row in df_ingredients.iterrows():
                # Parse JSONB fields
                nutritional_value = None
                if pd.notna(row.get("nutritional_value")) and row.get("nutritional_value"):
                    try:
                        nutritional_value = (
                            json.loads(row["nutritional_value"])
                            if isinstance(row["nutritional_value"], str)
                            else row["nutritional_value"]
                        )
                    except (json.JSONDecodeError, ValueError, TypeError):
                        nutritional_value = None

                common_allergens = None
                if pd.notna(row.get("common_allergens")) and row.get("common_allergens"):
                    try:
                        common_allergens = (
                            json.loads(row["common_allergens"])
                            if isinstance(row["common_allergens"], str)
                            else row["common_allergens"]
                        )
                    except (json.JSONDecodeError, ValueError, TypeError):
                        common_allergens = None

                ingredient = Ingredient(
                    id=int(row["id"]),
                    name=row["name"],
                    description=row.get("description") if pd.notna(row.get("description")) else None,
                    nutritional_value=nutritional_value,
                    common_allergens=common_allergens,
                )
                session.add(ingredient)
                ingredients_map[int(row["id"])] = int(row["id"])

            await session.commit()

            # Reset sequence for ingredients
            await session.execute(text("SELECT setval('ingredient_id_seq', (SELECT MAX(id) FROM ingredient))"))
            await session.commit()

            print(f"✓ Restored {len(df_ingredients)} ingredients")
            print()

            # Step 3: Restore products
            print("Restoring products...")
            df_products = pd.read_csv(products_csv)

            for _, row in df_products.iterrows():
                product = CatFoodProduct(
                    id=int(row["id"]),
                    name=row["name"],
                    brand=row["brand"],
                    price=float(row["price"]) if pd.notna(row.get("price")) else None,
                    age_group=row.get("age_group") if pd.notna(row.get("age_group")) else None,
                    food_type=row.get("food_type") if pd.notna(row.get("food_type")) else None,
                    description=row.get("description") if pd.notna(row.get("description")) else None,
                    full_ingredient_list=(
                        row.get("full_ingredient_list") if pd.notna(row.get("full_ingredient_list")) else None
                    ),
                    image_url=row.get("image_url") if pd.notna(row.get("image_url")) else None,
                    shopping_url=row.get("shopping_url") if pd.notna(row.get("shopping_url")) else None,
                    embedding_id=row.get("embedding_id") if pd.notna(row.get("embedding_id")) else None,
                )
                session.add(product)

            await session.commit()

            # Reset sequence for products
            await session.execute(
                text("SELECT setval('cat_food_product_id_seq', (SELECT MAX(id) FROM cat_food_product))")
            )
            await session.commit()

            print(f"✓ Restored {len(df_products)} products")
            print()

            # Step 4: Restore associations
            print("Restoring product-ingredient associations...")
            df_associations = pd.read_csv(associations_csv)

            # Use raw SQL to insert associations since it's a table, not a model
            associations_to_insert = []
            for _, row in df_associations.iterrows():
                product_id = int(row["product_id"])
                ingredient_id = int(row["ingredient_id"])
                associations_to_insert.append((product_id, ingredient_id))

            if associations_to_insert:
                # Insert in batches of 1000 to avoid query size limits
                batch_size = 1000
                for i in range(0, len(associations_to_insert), batch_size):
                    batch = associations_to_insert[i : i + batch_size]
                    values_str = ",".join([f"({pid},{iid})" for pid, iid in batch])
                    await session.execute(
                        text(
                            f"""
                            INSERT INTO product_ingredient_association (product_id, ingredient_id)
                            VALUES {values_str}
                            ON CONFLICT DO NOTHING
                        """
                        )
                    )
                await session.commit()

            print(f"✓ Restored {len(associations_to_insert)} associations")
            print()

            # Step 5: Verify restoration
            print("Verifying restoration...")
            result = await session.execute(select(CatFoodProduct))
            product_count = len(result.scalars().all())

            result = await session.execute(select(Ingredient))
            ingredient_count = len(result.scalars().all())

            result = await session.execute(select(product_ingredient_association))
            association_count = len(result.fetchall())

            print("✓ Verification complete:")
            print(f"  Products: {product_count}")
            print(f"  Ingredients: {ingredient_count}")
            print(f"  Associations: {association_count}")

    except Exception as e:
        print(f"❌ Error during restoration: {e}")
        raise
    finally:
        await engine.dispose()

    print()
    print("=" * 80)
    print("RESTORATION COMPLETE")
    print("=" * 80)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Restore database from CSV backup files")
    parser.add_argument("--backup-dir", type=str, required=True, help="Path to backup directory containing CSV files")

    args = parser.parse_args()

    print("⚠️  WARNING: This will DELETE all existing data and restore from backup!")
    print()
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        print("Cancelled.")
        return

    await restore_from_backup(args.backup_dir)


if __name__ == "__main__":
    asyncio.run(main())
