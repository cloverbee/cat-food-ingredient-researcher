"""
Backup database tables to CSV files before importing new data.

This script exports all data from key tables (products, ingredients, associations)
to CSV files for backup purposes before running data imports.

Usage:
    python -m src.scripts.backup_database
    python -m src.scripts.backup_database --output-dir backups/2024-01-15
"""

import argparse
import asyncio
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings
from src.domain.models.ingredient import Ingredient
from src.domain.models.product import CatFoodProduct, product_ingredient_association


async def backup_table_to_csv(engine, table_name: str, output_path: Path) -> int:
    """Backup a table to CSV file."""
    async with engine.connect() as conn:
        # Get all data from table
        result = await conn.execute(text(f'SELECT * FROM "{table_name}"'))
        rows = result.fetchall()
        # Get column names from result keys (SQLAlchemy async API)
        column_names = list(result.keys())

        if not rows:
            print(f"  ⚠️  Table '{table_name}' is empty")
            # Create empty CSV with headers
            df = pd.DataFrame(columns=column_names)
            df.to_csv(output_path, index=False)
            return 0

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=column_names)

        # Save to CSV
        df.to_csv(output_path, index=False)

        print(f"  ✅ Backed up {len(df)} rows from '{table_name}' to {output_path.name}")
        return len(df)


async def backup_database(output_dir: Path = None) -> dict:
    """
    Backup all key database tables to CSV files.

    Returns a dictionary with backup statistics.
    """
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"backups/{timestamp}")

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("DATABASE BACKUP")
    print("=" * 80)
    print(f"Output directory: {output_dir}")
    print()

    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    stats = {}

    try:
        # Backup products table
        products_path = output_dir / "cat_food_product.csv"
        stats["products"] = await backup_table_to_csv(engine, "cat_food_product", products_path)

        # Backup ingredients table
        ingredients_path = output_dir / "ingredient.csv"
        stats["ingredients"] = await backup_table_to_csv(engine, "ingredient", ingredients_path)

        # Backup product-ingredient associations
        association_path = output_dir / "product_ingredient_association.csv"
        stats["associations"] = await backup_table_to_csv(engine, "product_ingredient_association", association_path)

        # Backup users table (if exists)
        try:
            users_path = output_dir / "user.csv"
            stats["users"] = await backup_table_to_csv(engine, "user", users_path)
        except Exception as e:
            print(f"  ⚠️  Could not backup 'user' table: {e}")
            stats["users"] = 0

        # Create a summary file
        summary_path = output_dir / "backup_summary.txt"
        with open(summary_path, "w") as f:
            f.write("Database Backup Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(
                f"Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'hidden'}\n\n"
            )
            f.write("Table Statistics:\n")
            f.write(f"  Products: {stats['products']} rows\n")
            f.write(f"  Ingredients: {stats['ingredients']} rows\n")
            f.write(f"  Associations: {stats['associations']} rows\n")
            if stats.get("users", 0) > 0:
                f.write(f"  Users: {stats['users']} rows\n")

        print()
        print("=" * 80)
        print("BACKUP SUMMARY")
        print("=" * 80)
        print(f"Products: {stats['products']} rows")
        print(f"Ingredients: {stats['ingredients']} rows")
        print(f"Associations: {stats['associations']} rows")
        if stats.get("users", 0) > 0:
            print(f"Users: {stats['users']} rows")
        print()
        print(f"✅ Backup complete! Files saved to: {output_dir}")
        print(f"📄 Summary: {summary_path}")

    except Exception as e:
        print(f"❌ Error during backup: {e}")
        raise
    finally:
        await engine.dispose()

    return stats


async def main_async():
    """Main async function."""
    parser = argparse.ArgumentParser(description="Backup database tables to CSV files before importing new data")
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for backup files (default: backups/YYYYMMDD_HHMMSS)",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    await backup_database(output_dir)


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
