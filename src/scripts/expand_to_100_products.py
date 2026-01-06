"""
Expand cat food product database to 100 items from multiple sources.

This script:
1. Checks current product count in the database
2. Fetches products from multiple sources (Amazon, Petco, Chewy, Rainforest API)
3. Ensures we reach 100 total products
4. Handles duplicates by checking existing products
5. Imports new products into the database

Usage:
    python -m src.scripts.expand_to_100_products
    python -m src.scripts.expand_to_100_products --target 100 --dry-run
"""

import argparse
import asyncio
import csv
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import func, select

from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct
from src.domain.repositories.ingredient_repository import IngredientRepository
from src.domain.repositories.product_repository import ProductRepository
from src.domain.schemas.product import ProductCreate
from src.domain.services.ingestion_service import IngestionService
from src.domain.services.ingredient_service import IngredientService
from src.domain.services.product_service import ProductService

# Import scrapers
from src.scripts.fetch_cat_food_data import AmazonScraper
from src.scripts.fetch_cat_food_data import CatFoodProduct as ScrapedProduct
from src.scripts.fetch_cat_food_data import ChewyScraper, PetcoScraper

# Try to import API fetchers
try:
    from src.scripts.rainforest_api_fetcher import fetch_cat_food as fetch_rainforest

    RAINFOREST_AVAILABLE = True
except (ImportError, AttributeError):
    RAINFOREST_AVAILABLE = False
    fetch_rainforest = None

try:
    from src.scripts.amazon_api_fetcher import create_amazon_api, search_amazon_products

    AMAZON_API_AVAILABLE = True
except (ImportError, AttributeError):
    AMAZON_API_AVAILABLE = False
    create_amazon_api = None
    search_amazon_products = None


async def get_current_product_count() -> int:
    """Get the current number of products in the database."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(CatFoodProduct.id)))
        count = result.scalar() or 0
        return count


async def get_existing_product_urls() -> Set[str]:
    """Get all existing shopping URLs to avoid duplicates."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(CatFoodProduct.shopping_url))
        urls = {url for url in result.scalars() if url}
        return urls


async def get_existing_product_names() -> Set[str]:
    """Get all existing product names (normalized) to avoid duplicates."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(CatFoodProduct.name))
        names = {name.lower().strip() for name in result.scalars() if name}
        return names


def normalize_url(url: Optional[str]) -> Optional[str]:
    """Normalize URL for comparison."""
    if not url:
        return None
    # Remove query parameters and fragments for comparison
    url = url.split("?")[0].split("#")[0]
    return url.strip().lower()


def is_duplicate(product: ScrapedProduct, existing_urls: Set[str], existing_names: Set[str]) -> bool:
    """Check if a product is a duplicate."""
    # Check by URL
    normalized_url = normalize_url(product.shopping_url)
    if normalized_url and normalized_url in existing_urls:
        return True

    # Check by name (normalized)
    normalized_name = (product.name or "").lower().strip()
    if normalized_name and normalized_name in existing_names:
        return True

    return False


def fetch_from_scrapers(
    sources: List[str], food_types: List[str], count_per_source: int, delay: float = 2.0, max_retries: int = 3
) -> List[ScrapedProduct]:
    """Fetch products using web scrapers with retry logic."""
    all_products: List[ScrapedProduct] = []

    scraper_map = {
        "amazon": AmazonScraper,
        "chewy": ChewyScraper,
        "petco": PetcoScraper,
    }

    for source in sources:
        if source not in scraper_map:
            print(f"⚠️  Unknown scraper source: {source}")
            continue

        scraper_class = scraper_map[source]
        scraper = scraper_class(delay=delay)

        for food_type in food_types:
            print(f"🔍 Fetching {food_type} products from {source}...")

            # Retry logic with exponential backoff
            products = []
            for attempt in range(max_retries):
                try:
                    products = scraper.fetch("cat food", food_type, count_per_source)
                    if products:
                        break  # Success, exit retry loop
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Too Many Requests" in error_msg:
                        wait_time = delay * (2**attempt)  # Exponential backoff
                        print(f"  ⚠️  Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {wait_time:.1f}s...")
                        if attempt < max_retries - 1:
                            time.sleep(wait_time)
                            continue
                    elif "503" in error_msg or "Service Unavailable" in error_msg:
                        wait_time = delay * (2**attempt)
                        print(
                            f"  ⚠️  Service unavailable (attempt {attempt + 1}/{max_retries}). Waiting {wait_time:.1f}s..."
                        )
                        if attempt < max_retries - 1:
                            time.sleep(wait_time)
                            continue
                    elif "403" in error_msg or "Forbidden" in error_msg:
                        print(f"  ❌ Access forbidden. {source} may be blocking scrapers.")
                        break  # Don't retry 403 errors
                    else:
                        print(f"  ⚠️  Error (attempt {attempt + 1}/{max_retries}): {error_msg}")
                        if attempt < max_retries - 1:
                            time.sleep(delay * (attempt + 1))
                            continue

            if products:
                # Normalize food type
                for p in products:
                    p.food_type = scraper.normalize_food_type(food_type)
                all_products.extend(products)
                print(f"  ✅ Fetched {len(products)} products from {source} ({food_type})")
            else:
                print(f"  ⚠️  No products fetched from {source} ({food_type}) - may be rate limited or blocked")

            time.sleep(delay)  # Rate limiting between sources

    return all_products


def fetch_from_rainforest_api(food_types: List[str], count_per_type: int) -> List[Dict]:
    """Fetch products using Rainforest API."""
    if not RAINFOREST_AVAILABLE or fetch_rainforest is None:
        print("⚠️  Rainforest API not available (module not imported)")
        return []

    try:
        api_key = os.getenv("RAINFOREST_API_KEY")
        if not api_key:
            print("⚠️  RAINFOREST_API_KEY not set, skipping Rainforest API")
            return []

        all_products = []
        for food_type in food_types:
            print(f"🔍 Fetching {food_type} products from Rainforest API...")
            try:
                products = fetch_rainforest(api_key, food_type, count_per_type)
                all_products.extend(products)
                print(f"  ✅ Fetched {len(products)} products from Rainforest API ({food_type})")
            except Exception as e:
                print(f"  ❌ Error fetching from Rainforest API ({food_type}): {e}")
                continue

        return all_products
    except Exception as e:
        print(f"⚠️  Error with Rainforest API: {e}")
        return []


def fetch_from_amazon_api(food_types: List[str], count_per_type: int) -> List[Dict]:
    """Fetch products using Amazon Product Advertising API."""
    if not AMAZON_API_AVAILABLE or create_amazon_api is None or search_amazon_products is None:
        print("⚠️  Amazon API not available (module not imported)")
        return []

    try:
        amazon, partner_tag = create_amazon_api()

        all_products = []
        for food_type in food_types:
            print(f"🔍 Fetching {food_type} products from Amazon API...")
            try:
                if food_type == "dry":
                    query = "cat dry food kibble"
                elif food_type == "wet":
                    query = "cat wet food canned"
                else:
                    query = "cat treats dessert"

                products = search_amazon_products(amazon, partner_tag, query, food_type, count_per_type)
                all_products.extend(products)
                print(f"  ✅ Fetched {len(products)} products from Amazon API ({food_type})")
            except Exception as e:
                print(f"  ❌ Error fetching from Amazon API ({food_type}): {e}")
                continue

        return all_products
    except Exception as e:
        print(f"⚠️  Error with Amazon API: {e}")
        return []


def convert_to_scraped_product(product_dict: Dict) -> ScrapedProduct:
    """Convert a dictionary product to ScrapedProduct."""
    # Handle price conversion
    price = product_dict.get("price")
    if price and isinstance(price, str):
        try:
            price = float(price.replace("$", "").replace(",", "").strip())
        except (ValueError, AttributeError):
            price = None
    elif not price:
        price = None

    return ScrapedProduct(
        name=product_dict.get("name", "Unknown"),
        brand=product_dict.get("brand", "Unknown"),
        price=price,
        age_group=product_dict.get("age_group"),
        food_type=product_dict.get("food_type"),
        description=product_dict.get("description"),
        full_ingredient_list=product_dict.get("full_ingredient_list"),
        image_url=product_dict.get("image_url"),
        shopping_url=product_dict.get("shopping_url"),
    )


def load_products_from_csv(csv_path: Path) -> List[ScrapedProduct]:
    """Load products from a CSV file."""
    products = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert CSV row to dict format
                product_dict = {
                    "name": row.get("name", ""),
                    "brand": row.get("brand", ""),
                    "price": row.get("price") or None,
                    "age_group": row.get("age_group") or None,
                    "food_type": row.get("food_type") or None,
                    "description": row.get("description") or None,
                    "full_ingredient_list": row.get("full_ingredient_list") or None,
                    "image_url": row.get("image_url") or None,
                    "shopping_url": row.get("shopping_url") or None,
                }
                products.append(convert_to_scraped_product(product_dict))
        return products
    except Exception as e:
        print(f"  ⚠️  Error loading CSV {csv_path}: {e}")
        return []


async def import_products_to_db(products: List[ScrapedProduct], dry_run: bool = False) -> Tuple[int, int]:
    """Import products into the database. Returns (imported_count, skipped_count)."""
    if not products:
        return 0, 0

    # Get existing products to avoid duplicates
    existing_urls = await get_existing_product_urls()
    existing_names = await get_existing_product_names()

    # Filter out duplicates
    new_products = []
    skipped = 0

    for product in products:
        if is_duplicate(product, existing_urls, existing_names):
            skipped += 1
            continue

        new_products.append(product)
        # Update tracking sets
        normalized_url = normalize_url(product.shopping_url)
        if normalized_url:
            existing_urls.add(normalized_url)
        normalized_name = (product.name or "").lower().strip()
        if normalized_name:
            existing_names.add(normalized_name)

    if dry_run:
        print("\n📊 Dry run results:")
        print(f"  Would import: {len(new_products)} products")
        print(f"  Would skip: {skipped} duplicates")
        return len(new_products), skipped

    if not new_products:
        print("\n⚠️  No new products to import (all are duplicates)")
        return 0, skipped

    # Save to CSV first (for backup and inspection)
    csv_path = Path("expanded_products.csv")
    save_products_to_csv(new_products, csv_path)

    # Import using ingestion service
    async with AsyncSessionLocal() as db:
        product_repo = ProductRepository(db)
        ingredient_repo = IngredientRepository(db)
        product_service = ProductService(product_repo)
        ingredient_service = IngredientService(ingredient_repo)
        ingestion_service = IngestionService(product_service, ingredient_service)

        # Convert to CSV format for ingestion
        csv_content = csv_path.read_text(encoding="utf-8")
        result = await ingestion_service.ingest_csv_content(csv_content)

        imported_count = result.get("products_created", len(new_products))
        print(f"\n✅ Imported {imported_count} products into database")
        print(f"📁 Products saved to: {csv_path}")

        return imported_count, skipped


def save_products_to_csv(products: List[ScrapedProduct], filename: Path):
    """Save products to CSV file."""
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

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            writer.writerow(
                {
                    "name": product.name or "",
                    "brand": product.brand or "",
                    "price": product.price or "",
                    "age_group": product.age_group or "",
                    "food_type": product.food_type or "",
                    "description": product.description or "",
                    "full_ingredient_list": product.full_ingredient_list or "",
                    "image_url": product.image_url or "",
                    "shopping_url": product.shopping_url or "",
                }
            )


async def main_async():
    """Main async function."""
    parser = argparse.ArgumentParser(
        description="Expand cat food product database to target count from multiple sources"
    )
    parser.add_argument(
        "--target",
        type=int,
        default=100,
        help="Target total number of products (default: 100)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without actually importing",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["amazon", "chewy", "petco"],
        choices=["amazon", "chewy", "petco", "rainforest", "amazon-api"],
        help="Sources to fetch from (default: amazon chewy petco)",
    )
    parser.add_argument(
        "--food-types",
        nargs="+",
        default=["dry", "wet", "dessert"],
        choices=["dry", "wet", "dessert"],
        help="Food types to fetch (default: dry wet dessert)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay between requests for scrapers (seconds, default: 3.0)",
    )
    parser.add_argument(
        "--use-csv-fallback",
        action="store_true",
        help="Use existing CSV files as fallback if scrapers fail",
    )
    parser.add_argument(
        "--csv-files",
        nargs="+",
        help="Specific CSV files to use as fallback (e.g., cat_food_popular_merged.csv)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Expand Cat Food Product Database")
    print("=" * 70)

    # Check current count
    current_count = await get_current_product_count()
    print(f"\n📊 Current database count: {current_count} products")
    print(f"🎯 Target count: {args.target} products")

    needed = max(0, args.target - current_count)
    if needed == 0:
        print(f"\n✅ Already at or above target count ({current_count} >= {args.target})")
        return

    print(f"📦 Need to fetch: {needed} more products")
    print(f"🔍 Sources: {', '.join(args.sources)}")
    print(f"🍽️  Food types: {', '.join(args.food_types)}")
    print("=" * 70)
    print()

    # Fetch products from multiple sources
    all_products: List[ScrapedProduct] = []

    # Calculate how many to fetch per source/type
    scraper_sources = [s for s in args.sources if s in ["amazon", "chewy", "petco"]]
    api_sources = [s for s in args.sources if s in ["rainforest", "amazon-api"]]

    # Prioritize API sources (more reliable)
    # Fetch from Rainforest API first
    if "rainforest" in args.sources:
        count_per_type = max(15, needed // len(args.food_types) + 10)
        print(f"📥 Fetching from Rainforest API: {count_per_type} per type...")
        rainforest_products = fetch_from_rainforest_api(args.food_types, count_per_type)
        converted_rainforest = [convert_to_scraped_product(p) for p in rainforest_products]
        all_products.extend(converted_rainforest)
        print(f"✅ Total from Rainforest API: {len(converted_rainforest)} products\n")

    # Fetch from Amazon API
    if "amazon-api" in args.sources:
        count_per_type = max(15, needed // len(args.food_types) + 10)
        print(f"📥 Fetching from Amazon API: {count_per_type} per type...")
        amazon_api_products = fetch_from_amazon_api(args.food_types, count_per_type)
        converted_amazon = [convert_to_scraped_product(p) for p in amazon_api_products]
        all_products.extend(converted_amazon)
        print(f"✅ Total from Amazon API: {len(converted_amazon)} products\n")

    # Fetch from scrapers (less reliable, may be rate limited)
    if scraper_sources:
        count_per_source_type = max(10, needed // (len(scraper_sources) * len(args.food_types)) + 5)
        print(f"📥 Fetching from scrapers: {count_per_source_type} per source/type...")
        print("⚠️  Note: Web scrapers may be rate limited. Consider using API sources instead.")
        scraper_products = fetch_from_scrapers(scraper_sources, args.food_types, count_per_source_type, args.delay)
        all_products.extend(scraper_products)
        print(f"✅ Total from scrapers: {len(scraper_products)} products\n")

    print(f"📦 Total products fetched from APIs/Scrapers: {len(all_products)}")

    # CSV fallback if enabled and we don't have enough products
    if (args.use_csv_fallback or args.csv_files) and len(all_products) < needed:
        csv_files_to_check = []

        if args.csv_files:
            csv_files_to_check = [Path(f) for f in args.csv_files]
        else:
            # Check common CSV files
            common_csvs = [
                "cat_food_popular_merged.csv",
                "cat_food_rainforest.csv",
                "cat_food_popular_merged.csv",
            ]
            csv_files_to_check = [Path(f) for f in common_csvs if Path(f).exists()]

        if csv_files_to_check:
            print("\n📂 Loading products from CSV files (fallback)...")
            csv_products = []
            for csv_file in csv_files_to_check:
                if csv_file.exists():
                    print(f"  📄 Loading from {csv_file}...")
                    products = load_products_from_csv(csv_file)
                    csv_products.extend(products)
                    print(f"    ✅ Loaded {len(products)} products from {csv_file}")

            if csv_products:
                all_products.extend(csv_products)
                print(f"✅ Total from CSV files: {len(csv_products)} products\n")

    print(f"📦 Total products fetched: {len(all_products)}")

    if not all_products:
        print("\n❌ No products were fetched.")
        print("\n💡 Suggestions:")
        print("  1. Use API sources (more reliable):")
        print("     python -m src.scripts.expand_to_100_products --sources rainforest amazon-api")
        print("  2. Use CSV fallback:")
        print("     python -m src.scripts.expand_to_100_products --use-csv-fallback")
        print("  3. Increase delay to avoid rate limits:")
        print("     python -m src.scripts.expand_to_100_products --delay 5.0")
        print("  4. Check your API keys if using API sources")
        return

    # Import products
    imported, skipped = await import_products_to_db(all_products, dry_run=args.dry_run)

    # Final count
    if not args.dry_run:
        final_count = await get_current_product_count()
        print(f"\n📊 Final database count: {final_count} products")
        print(f"✅ Successfully expanded database by {imported} products")
        if skipped > 0:
            print(f"⚠️  Skipped {skipped} duplicate products")
    else:
        print(f"\n📊 Would result in: {current_count + imported} products")

    print("=" * 70)


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
