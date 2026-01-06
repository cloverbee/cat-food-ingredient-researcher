"""
Rollback database to original 38 products.

This script deletes all products with ID > 38, keeping only the original 38 items.

Usage:
    python -m src.scripts.rollback_to_38_products --yes
"""

import argparse
import asyncio

from sqlalchemy import delete, func, select, text

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct, product_ingredient_association


async def get_product_count() -> int:
    """Get current product count."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(CatFoodProduct.id)))
        count = result.scalar() or 0
        return count


async def rollback_to_38_products(confirm: bool = False) -> int:
    """
    Delete all products with ID > 38, keeping only the original 38.

    Returns the number of products deleted.
    """
    if not confirm:
        raise ValueError("Must pass confirm=True to delete products")

    async with AsyncSessionLocal() as db:
        # First, check current count
        count_result = await db.execute(select(func.count(CatFoodProduct.id)))
        current_count = count_result.scalar() or 0

        if current_count <= 38:
            print(f"✅ Database already has {current_count} products (≤ 38). Nothing to delete.")
            return 0

        # Get IDs of products to delete (ID > 38)
        ids_result = await db.execute(select(CatFoodProduct.id).where(CatFoodProduct.id > 38))
        ids_to_delete = [row[0] for row in ids_result.fetchall()]

        if not ids_to_delete:
            print("✅ No products with ID > 38 found. Nothing to delete.")
            return 0

        print(f"📊 Current count: {current_count} products")
        print(f"🗑️  Will delete {len(ids_to_delete)} products (IDs: {min(ids_to_delete)}-{max(ids_to_delete)})")
        print(f"✅ Will keep {38} products (IDs: 1-38)")

        # Delete from association table first (due to FK constraints)
        await db.execute(
            delete(product_ingredient_association).where(product_ingredient_association.c.product_id.in_(ids_to_delete))
        )

        # Delete products
        await db.execute(delete(CatFoodProduct).where(CatFoodProduct.id.in_(ids_to_delete)))

        await db.commit()

        # Verify final count
        final_result = await db.execute(select(func.count(CatFoodProduct.id)))
        final_count = final_result.scalar() or 0

        print(f"✅ Rollback complete! Final count: {final_count} products")

        return len(ids_to_delete)


async def list_products_to_delete() -> None:
    """List products that would be deleted (dry run)."""
    async with AsyncSessionLocal() as db:
        count_result = await db.execute(select(func.count(CatFoodProduct.id)))
        current_count = count_result.scalar() or 0

        print(f"📊 Current database count: {current_count} products")

        if current_count <= 38:
            print(f"✅ Database already has {current_count} products (≤ 38). Nothing to delete.")
            return

        # Get products that would be deleted
        products_result = await db.execute(
            select(CatFoodProduct.id, CatFoodProduct.name, CatFoodProduct.brand, CatFoodProduct.shopping_url)
            .where(CatFoodProduct.id > 38)
            .order_by(CatFoodProduct.id)
        )

        products_to_delete = products_result.fetchall()

        print(f"\n🗑️  Products that would be deleted ({len(products_to_delete)}):")
        print("=" * 80)
        for product_id, name, brand, shopping_url in products_to_delete:
            print(f"  ID {product_id}: {brand} - {name}")
            if shopping_url:
                print(f"    URL: {shopping_url[:60]}...")

        print("\n✅ Products that would be kept (IDs 1-38):")
        print("=" * 80)
        kept_result = await db.execute(
            select(CatFoodProduct.id, CatFoodProduct.name, CatFoodProduct.brand)
            .where(CatFoodProduct.id <= 38)
            .order_by(CatFoodProduct.id)
        )
        kept_products = kept_result.fetchall()
        for product_id, name, brand in kept_products:
            print(f"  ID {product_id}: {brand} - {name}")


async def main_async():
    """Main async function."""
    parser = argparse.ArgumentParser(
        description="Rollback database to original 38 products (delete all products with ID > 38)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required. Confirm you want to delete products with ID > 38.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting.",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("=" * 80)
        print("DRY RUN - No changes will be made")
        print("=" * 80)
        await list_products_to_delete()
        return

    if not args.yes:
        print("⚠️  This will delete all products with ID > 38.")
        print("📋 Run with --dry-run to see what would be deleted.")
        print("✅ Run with --yes to confirm deletion.")
        raise SystemExit("Refusing to delete without --yes confirmation.")

    print("=" * 80)
    print("Rollback to 38 Products")
    print("=" * 80)

    deleted_count = await rollback_to_38_products(confirm=True)

    if deleted_count > 0:
        print(f"\n✅ Successfully rolled back! Deleted {deleted_count} products.")
        print("✅ Database now contains only the original 38 products (IDs 1-38).")
    else:
        print("\n✅ No products were deleted (already at or below 38 products).")


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
