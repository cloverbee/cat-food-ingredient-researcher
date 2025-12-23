"""
Amazon Product Advertising API Fetcher

This script uses the Amazon Product Advertising API via python-amazon-paapi
to fetch cat food products.

Requires API credentials (Access Key, Secret Key, Associate Tag).  # pragma: allowlist secret

Setup:
1. Sign up for Amazon Product Advertising API: https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html
2. Get your credentials (Access Key, Secret Key, Associate Tag)
3. Set environment variables:
   - AMAZON_ACCESS_KEY
   - AMAZON_SECRET_KEY
   - AMAZON_ASSOCIATE_TAG

Or use a .env file with these variables.

Usage:
    python -m src.scripts.amazon_api_fetcher --type dry --count 100
"""

import argparse
import contextlib
import csv
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional

# Handle dotenv import
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore

# Handle amazon_paapi import
try:
    from amazon_paapi import AmazonApi
    from amazon_paapi.errors import AmazonError

    AMAZON_PAAPI_AVAILABLE = True
except ImportError:
    AMAZON_PAAPI_AVAILABLE = False
    AmazonApi = None  # type: ignore
    AmazonError = Exception  # type: ignore

# Load .env file if it exists
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists() and load_dotenv:
    try:
        load_dotenv(env_path)
    except Exception as e:
        print(f"⚠️  Warning: Could not load .env file: {e}")


def get_amazon_credentials() -> tuple:
    """Get Amazon API credentials from environment variables."""
    access_key = os.getenv("AMAZON_ACCESS_KEY")
    secret_key = os.getenv("AMAZON_SECRET_KEY")
    partner_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
    country = os.getenv("AMAZON_COUNTRY", "US")  # Default to US

    if not all([access_key, secret_key, partner_tag]):
        raise ValueError(
            "Missing Amazon API credentials. Set AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, and AMAZON_ASSOCIATE_TAG"
        )

    return access_key, secret_key, partner_tag, country


def create_amazon_api() -> Any:
    """Create and return an AmazonApi instance."""
    if not AMAZON_PAAPI_AVAILABLE:
        raise ImportError("python-amazon-paapi is required. Install with: pip install python-amazon-paapi")

    access_key, secret_key, partner_tag, country = get_amazon_credentials()

    amazon = AmazonApi(access_key, secret_key, partner_tag, country)
    return amazon, partner_tag


def search_amazon_products(amazon: Any, partner_tag: str, query: str, food_type: str, count: int) -> List[dict]:
    """Search for products on Amazon with pagination support."""
    if not AMAZON_PAAPI_AVAILABLE:
        raise ImportError("python-amazon-paapi is required for Amazon API access")

    products = []
    max_items_per_request = 10  # Amazon API limit
    item_page = 1
    seen_asins = set()  # Track ASINs to avoid duplicates

    print(f"Fetching up to {count} products (Amazon API returns max {max_items_per_request} per request)...")

    while len(products) < count:
        try:
            items_to_fetch = min(max_items_per_request, count - len(products))

            # Use python-amazon-paapi search
            search_result = amazon.search_items(
                keywords=query,
                search_index="PetSupplies",
                item_count=items_to_fetch,
                item_page=item_page,
            )

            if not search_result or not search_result.items:
                print(f"No more results found. Retrieved {len(products)} products.")
                break

            new_products_count = 0
            for item in search_result.items:
                # Get ASIN to check for duplicates and create affiliate links
                asin = getattr(item, "asin", None)

                if asin and asin in seen_asins:
                    continue  # Skip duplicates

                if asin:
                    seen_asins.add(asin)

                # Extract image URL
                image_url = None
                if hasattr(item, "images") and item.images:
                    primary = getattr(item.images, "primary", None)
                    if primary:
                        large = getattr(primary, "large", None)
                        if large:
                            image_url = getattr(large, "url", None)
                    # Fallback to variants if primary not available
                    if not image_url:
                        variants = getattr(item.images, "variants", None)
                        if variants and len(variants) > 0:
                            large_variant = getattr(variants[0], "large", None)
                            if large_variant:
                                image_url = getattr(large_variant, "url", None)

                # Generate affiliate shopping link
                shopping_url = None
                if asin and partner_tag:
                    shopping_url = f"https://www.amazon.com/dp/{asin}?tag={partner_tag}"

                # Extract product info
                item_info = getattr(item, "item_info", None)

                # Get title
                name = "Unknown"
                if item_info:
                    title_obj = getattr(item_info, "title", None)
                    if title_obj:
                        name = getattr(title_obj, "display_value", "Unknown")

                # Get brand
                brand = "Unknown"
                if item_info:
                    by_line_info = getattr(item_info, "by_line_info", None)
                    if by_line_info:
                        brand_obj = getattr(by_line_info, "brand", None)
                        if brand_obj:
                            brand = getattr(brand_obj, "display_value", "Unknown")

                product_data = {
                    "name": name,
                    "brand": brand,
                    "price": None,
                    "age_group": None,
                    "food_type": food_type.capitalize(),
                    "description": None,
                    "full_ingredient_list": None,
                    "image_url": image_url,
                    "shopping_url": shopping_url,
                }

                # Extract price
                offers = getattr(item, "offers", None)
                if offers:
                    listings = getattr(offers, "listings", None)
                    if listings and len(listings) > 0:
                        price_obj = getattr(listings[0], "price", None)
                        if price_obj:
                            display_amount = getattr(price_obj, "display_amount", None)
                            if display_amount:
                                with contextlib.suppress(ValueError, AttributeError):
                                    product_data["price"] = float(display_amount.replace("$", "").replace(",", ""))

                # Extract description from features
                if item_info:
                    features = getattr(item_info, "features", None)
                    if features:
                        display_values = getattr(features, "display_values", None)
                        if display_values:
                            product_data["description"] = " ".join(display_values[:3])

                # Try to extract age group from title/description
                title_lower = product_data["name"].lower()
                if "kitten" in title_lower or "young" in title_lower:
                    product_data["age_group"] = "Kitten"
                elif "senior" in title_lower or "mature" in title_lower:
                    product_data["age_group"] = "Senior"
                elif "adult" in title_lower:
                    product_data["age_group"] = "Adult"

                products.append(product_data)
                new_products_count += 1

            print(f"  Page {item_page}: Retrieved {new_products_count} products (Total: {len(products)})")

            # Check if we've reached the total or no more pages
            if len(search_result.items) < max_items_per_request:
                print(f"Reached end of results. Retrieved {len(products)} products.")
                break

            item_page += 1

            # Rate limiting - Amazon API has limits
            if len(products) < count:
                time.sleep(1)  # Small delay between requests

        except AmazonError as e:
            print(f"❌ Amazon API Error: {e}")
            error_str = str(e)
            if "429" in error_str or "Throttling" in error_str or "TooManyRequests" in error_str:
                print("Rate limit exceeded. Waiting 5 seconds...")
                time.sleep(5)
                continue
            else:
                break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

    return products[:count]  # Return exactly the requested count


def save_to_csv(products: List[dict], filename: str):
    """Save products to CSV."""
    if not products:
        print("No products to save")
        return

    fieldnames = [
        "name",
        "brand",
        "price",
        "age_group",
        "food_type",
        "description",
        "full_ingredient_list",
        "image_url",
        "shopping_url",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            writer.writerow(
                {
                    "name": product.get("name", ""),
                    "brand": product.get("brand", ""),
                    "price": product.get("price") or "",
                    "age_group": product.get("age_group") or "",
                    "food_type": product.get("food_type", ""),
                    "description": product.get("description") or "",
                    "full_ingredient_list": product.get("full_ingredient_list") or "",
                    "image_url": product.get("image_url") or "",
                    "shopping_url": product.get("shopping_url") or "",
                }
            )

    print(f"✅ Saved {len(products)} products to {filename}")


def main():
    """Main function."""
    if not AMAZON_PAAPI_AVAILABLE:
        print("❌ python-amazon-paapi is not installed.")
        print("Install it with: pip install python-amazon-paapi")
        return

    parser = argparse.ArgumentParser(
        description="Fetch cat food from Amazon Product Advertising API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 100 dry food products
  python -m src.scripts.amazon_api_fetcher --type dry --count 100

  # Fetch 100 wet food products with custom output
  python -m src.scripts.amazon_api_fetcher --type wet --count 100 --output wet_food.csv

  # Fetch 100 dessert/treat products
  python -m src.scripts.amazon_api_fetcher --type dessert --count 100

Setup:
  1. Sign up: https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html
  2. Get credentials (Access Key, Secret Key, Associate Tag)
  3. Set environment variables or add to .env file:
     AMAZON_ACCESS_KEY=your_access_key
     AMAZON_SECRET_KEY=your_secret_key
     AMAZON_ASSOCIATE_TAG=your_associate_tag
        """,
    )
    parser.add_argument("--type", choices=["dry", "wet", "dessert"], required=True, help="Food type")
    parser.add_argument("--count", type=int, default=100, help="Number of products to fetch (default: 100)")
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV filename (default: cat_food_{type}_amazon.csv)",
    )

    args = parser.parse_args()

    # Set default output filename if not provided
    if args.output is None:
        args.output = f"cat_food_{args.type}_amazon.csv"

    try:
        amazon, partner_tag = create_amazon_api()
    except ValueError as e:
        print(f"❌ {e}")
        print("\n📝 Setup Instructions:")
        print("=" * 60)
        print("1. Sign up for Amazon Product Advertising API:")
        print("   https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html")
        print("\n2. Get your credentials:")
        print("   - Access Key")
        print("   - Secret Key")  # pragma: allowlist secret
        print("   - Associate Tag (from Amazon Associates)")
        print("\n3. Set environment variables:")
        print("   export AMAZON_ACCESS_KEY='your_access_key'")
        print("   export AMAZON_SECRET_KEY='your_secret_key'")  # pragma: allowlist secret
        print("   export AMAZON_ASSOCIATE_TAG='your_associate_tag'")
        print("\n   OR add to .env file in project root:")
        print("   AMAZON_ACCESS_KEY=your_access_key")
        print("   AMAZON_SECRET_KEY=your_secret_key")
        print("   AMAZON_ASSOCIATE_TAG=your_associate_tag")
        print("=" * 60)
        return
    except ImportError as e:
        print(f"❌ {e}")
        return

    # Build better search queries based on food type
    if args.type == "dry":
        query = "cat dry food kibble"
    elif args.type == "wet":
        query = "cat wet food canned"
    else:  # dessert
        query = "cat treats dessert"

    print("=" * 60)
    print("Amazon Product Advertising API - Cat Food Fetcher")
    print("=" * 60)
    print(f"Search Query: {query}")
    print(f"Food Type: {args.type}")
    print(f"Target Count: {args.count}")
    print(f"Output File: {args.output}")
    print("=" * 60)
    print()

    products = search_amazon_products(amazon, partner_tag, query, args.type, args.count)

    if products:
        save_to_csv(products, args.output)
        print(f"\n✅ Successfully fetched {len(products)} products")
        print(f"📁 Saved to: {args.output}")
    else:
        print("\n❌ No products found")
        print("\nTroubleshooting:")
        print("- Check your API credentials")
        print("- Verify your Associate Tag is correct")
        print("- Check Amazon API status and rate limits")


if __name__ == "__main__":
    main()
