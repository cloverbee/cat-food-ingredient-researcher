"""
Clear existing cat food data from the database.

This deletes rows from:
- product_ingredient_association
- cat_food_product
- ingredient

It does NOT touch the user table or other tables.

Usage:
  python -m src.scripts.clear_cat_food_data --yes
"""

import argparse
import asyncio

from sqlalchemy import text

from src.core.database import AsyncSessionLocal


async def clear_cat_food_data() -> None:
    async with AsyncSessionLocal() as db:
        # Order matters due to FK constraints
        await db.execute(text("DELETE FROM product_ingredient_association"))
        await db.execute(text("DELETE FROM cat_food_product"))
        await db.execute(text("DELETE FROM ingredient"))
        await db.commit()


async def _main_async() -> None:
    parser = argparse.ArgumentParser(description="Clear cat food products + ingredients from the database")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required. Confirm you want to delete ALL products/ingredients.",
    )
    args = parser.parse_args()

    if not args.yes:
        raise SystemExit("Refusing to run without --yes (this deletes ALL products/ingredients).")

    await clear_cat_food_data()
    print("Cleared cat_food_product, ingredient, and product_ingredient_association.")


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
