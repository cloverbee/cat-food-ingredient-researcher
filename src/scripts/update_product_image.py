"""
Update a product's image URL by product name.

Usage:
  python -m src.scripts.update_product_image --name "Wellness Core Original Original: Deboned Turkey, Turkey Meal & Chicken Meal" --image-url "https://image.chewy.com/catalog/general/images/wellness-core-grain-free-original-formula-natural-dry-cat-food-11lb-bag/img-680920._AC_SX500_SY400_QL75_V1_.jpg"
"""

import argparse
import asyncio

from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct


async def update_product_image(product_name: str, image_url: str) -> dict:
    """
    Update a product's image URL by product name.

    Args:
        product_name: The name of the product to update
        image_url: The new image URL to set
    """
    async with AsyncSessionLocal() as db:
        # Find product by name (case-insensitive, partial match)
        stmt = select(CatFoodProduct).where(CatFoodProduct.name.ilike(f"%{product_name}%"))
        result = await db.execute(stmt)
        products = result.scalars().all()

        if not products:
            return {"success": False, "message": f"Product '{product_name}' not found in database"}

        # If multiple matches, try exact match first
        exact_match = None
        for p in products:
            if p.name.lower() == product_name.lower():
                exact_match = p
                break

        product = exact_match if exact_match else products[0]

        if len(products) > 1 and not exact_match:
            print(f"Warning: Multiple matches for '{product_name}', updating first match: '{product.name}'")

        # Update image URL
        old_image_url = product.image_url
        product.image_url = image_url

        await db.commit()
        await db.refresh(product)

        return {
            "success": True,
            "product_id": product.id,
            "product_name": product.name,
            "old_image_url": old_image_url,
            "new_image_url": product.image_url,
            "message": f"Successfully updated image URL for '{product.name}' (ID: {product.id})",
        }


async def _main_async() -> None:
    parser = argparse.ArgumentParser(description="Update a product's image URL by product name")
    parser.add_argument("--name", required=True, help="Product name to update (can be partial match)")
    parser.add_argument("--image-url", required=True, help="New image URL to set")
    args = parser.parse_args()

    result = await update_product_image(args.name, args.image_url)

    print("\n" + "=" * 50)
    if result["success"]:
        print("Update Successful!")
        print(f"  Product ID: {result['product_id']}")
        print(f"  Product Name: {result['product_name']}")
        print(f"  Old Image URL: {result['old_image_url']}")
        print(f"  New Image URL: {result['new_image_url']}")
    else:
        print("Update Failed!")
        print(f"  Error: {result['message']}")
    print("=" * 50)


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
