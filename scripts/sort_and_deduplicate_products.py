#!/usr/bin/env python3
"""
Sort products by description and remove duplicates.
Duplicates are defined as products with the same full_ingredient_list and description.
"""
import asyncio
import sys
from collections import defaultdict
from pathlib import Path

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import settings
from src.domain.models.product import CatFoodProduct


async def find_and_remove_duplicates():
    """Find and remove duplicate products based on full_ingredient_list and description."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Fetch all products
            result = await session.execute(select(CatFoodProduct).order_by(CatFoodProduct.id))
            products = result.scalars().all()

            print(f"Total products before deduplication: {len(products)}")

            # Group products by (full_ingredient_list, description)
            groups = defaultdict(list)

            for product in products:
                # Normalize description and full_ingredient_list (handle None)
                description = (product.description or "").strip()
                full_ingredient_list = (product.full_ingredient_list or "").strip()

                # Create a key: (full_ingredient_list, description)
                key = (full_ingredient_list, description)
                groups[key].append(product)

            # Find duplicates (groups with more than one product)
            duplicates_to_delete = []
            kept_products = []

            for key, product_list in groups.items():
                if len(product_list) > 1:
                    # Sort by ID and keep the first one (lowest ID)
                    product_list.sort(key=lambda p: p.id)
                    kept = product_list[0]
                    duplicates = product_list[1:]

                    kept_products.append(kept)
                    duplicates_to_delete.extend(duplicates)

                    print("\nDuplicate group found:")
                    print(
                        f"  Description: {key[1][:50]}..."
                        if len(key[1]) > 50
                        else f"  Description: {key[1] or '(empty)'}"
                    )
                    print(
                        f"  Full Ingredient List: {key[0][:50]}..."
                        if len(key[0]) > 50
                        else f"  Full Ingredient List: {key[0] or '(empty)'}"
                    )
                    print(f"  Keeping: Product ID {kept.id} ({kept.name})")
                    print(f"  Deleting: {[p.id for p in duplicates]} ({[p.name for p in duplicates]})")
                else:
                    kept_products.append(product_list[0])

            print(f"\n{'=' * 80}")
            print("Summary:")
            print(f"  Total products: {len(products)}")
            print(f"  Unique products: {len(kept_products)}")
            print(f"  Duplicates to delete: {len(duplicates_to_delete)}")
            print(f"{'=' * 80}")

            if duplicates_to_delete:
                # Delete duplicate products
                # First, delete from association table
                duplicate_ids = [p.id for p in duplicates_to_delete]

                await session.execute(
                    text(
                        """
                        DELETE FROM product_ingredient_association
                        WHERE product_id = ANY(:product_ids)
                    """
                    ),
                    {"product_ids": duplicate_ids},
                )

                # Then delete the products
                await session.execute(delete(CatFoodProduct).where(CatFoodProduct.id.in_(duplicate_ids)))

                await session.commit()
                print(f"\n✓ Deleted {len(duplicates_to_delete)} duplicate products")
            else:
                print("\n✓ No duplicates found")

            # Now show products sorted by description
            print(f"\n{'=' * 80}")
            print("Products sorted by description:")
            print(f"{'=' * 80}")

            result = await session.execute(
                select(CatFoodProduct).order_by(CatFoodProduct.description.nulls_last(), CatFoodProduct.id)
            )
            sorted_products = result.scalars().all()

            print(f"\n{'ID':<6} {'Brand':<20} {'Name':<40} {'Description':<50}")
            print("-" * 120)

            for product in sorted_products:
                desc = (
                    (product.description or "")[:47] + "..."
                    if product.description and len(product.description) > 50
                    else (product.description or "")
                )
                name = product.name[:37] + "..." if len(product.name) > 40 else product.name
                brand = product.brand[:17] + "..." if len(product.brand) > 20 else product.brand
                print(f"{product.id:<6} {brand:<20} {name:<40} {desc:<50}")

            print(f"\nTotal products after deduplication: {len(sorted_products)}")

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main entry point."""
    print("=" * 80)
    print("Sorting products by description and removing duplicates")
    print("=" * 80)
    print()
    print("This will:")
    print("  1. Find products with the same full_ingredient_list and description")
    print("  2. Keep the product with the lowest ID from each duplicate group")
    print("  3. Delete the other duplicates")
    print("  4. Display all products sorted by description")
    print()

    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        print("Cancelled.")
        return

    await find_and_remove_duplicates()


if __name__ == "__main__":
    asyncio.run(main())
