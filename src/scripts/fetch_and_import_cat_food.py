"""
Fetch cat food products (scraping) -> save to CSV -> import into the database.

Notes:
- Web scraping may violate site Terms of Service. Use responsibly.
- If you already have a CSV, use: python -m src.scripts.import_products_csv_to_db --csv your.csv

Usage:
  python -m src.scripts.fetch_and_import_cat_food --source amazon --type dry --count 50 --output cat_food_dry.csv
  python -m src.scripts.fetch_and_import_cat_food --source all --type wet --count 50 --delay 2.0
"""

import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.scripts.clear_cat_food_data import clear_cat_food_data
from src.scripts.fetch_cat_food_data import AmazonScraper, CatFoodProduct, ChewyScraper, PetcoScraper, save_to_csv
from src.scripts.import_products_csv_to_db import import_csv_file


def _canonical_brand_map() -> Dict[str, List[str]]:
    # Canonical brand -> match tokens (case-insensitive substring match)
    # (We include a few common variants to improve recall.)
    return {
        "Blue Buffalo": ["blue buffalo", "blue wilderness", "blue basics"],
        "Hill's": ["hill's", "hills", "science diet", "hill’s"],
        "Purina": ["purina", "pro plan", "purina one", "fancy feast", "friskies", "beyond"],
        "Wellness": ["wellness", "core", "wellness core"],
        "Instinct": ["instinct", "nature's variety", "nature’s variety"],
    }


def infer_canonical_brand(product_name: str, preferred_brands: List[str]) -> Optional[str]:
    name_l = (product_name or "").lower()
    brand_map = _canonical_brand_map()
    for canonical in preferred_brands:
        tokens = brand_map.get(canonical, [canonical.lower()])
        if any(t in name_l for t in tokens):
            return canonical
    return None


def brand_matches(product: CatFoodProduct, preferred_brands: List[str]) -> bool:
    # Prefer matching on name because scraped brand fields are often unreliable.
    if infer_canonical_brand(product.name, preferred_brands):
        return True
    brand_l = (product.brand or "").lower()
    return any(b.lower() in brand_l for b in preferred_brands)


def fetch_products(source: str, food_type: str, count: int, delay: float) -> List[CatFoodProduct]:
    sources = ["amazon", "chewy", "petco"] if source == "all" else [source]

    all_products: List[CatFoodProduct] = []
    for src in sources:
        if src == "amazon":
            scraper = AmazonScraper(delay=delay)
        elif src == "chewy":
            scraper = ChewyScraper(delay=delay)
        elif src == "petco":
            scraper = PetcoScraper(delay=delay)
        else:
            raise ValueError(f"Unknown source: {src}")

        products = scraper.fetch("cat food", food_type, count)
        # Normalize food type for all products
        for p in products:
            p.food_type = scraper.normalize_food_type(food_type)
        all_products.extend(products)
        print(f"Fetched {len(products)} products from {src}")

    return all_products


async def _main_async() -> None:
    parser = argparse.ArgumentParser(description="Fetch cat food products and import into the database")
    parser.add_argument("--source", choices=["amazon", "chewy", "petco", "all"], default="amazon", help="Data source")
    parser.add_argument("--type", choices=["dry", "wet", "dessert"], required=True, help="Food type")
    parser.add_argument("--count", type=int, default=50, help="Number of products per source to fetch")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests (seconds)")
    parser.add_argument("--output", default="cat_food_data.csv", help="Output CSV filename")
    parser.add_argument("--skip-import", action="store_true", help="Only fetch + write CSV; do not import into DB")
    parser.add_argument(
        "--brands",
        default="Blue Buffalo,Hill's,Purina,Wellness,Instinct",
        help='Comma-separated canonical brands to include (default: "Blue Buffalo,Hill\\\'s,Purina,Wellness,Instinct")',
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing products/ingredients from DB before importing",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required with --clear-existing. Confirms destructive delete.",
    )
    args = parser.parse_args()

    preferred_brands = [b.strip() for b in (args.brands or "").split(",") if b.strip()]

    print("=" * 60)
    print("Fetch -> CSV -> Import")
    print("=" * 60)
    print(f"Source: {args.source}")
    print(f"Type:   {args.type}")
    print(f"Count:  {args.count}")
    print(f"Delay:  {args.delay}")
    print(f"CSV:    {args.output}")
    print(f"Brands: {', '.join(preferred_brands) if preferred_brands else '(none)'}")
    print("=" * 60)
    print("\n⚠️  LEGAL NOTICE:")
    print("Web scraping may violate Terms of Service.")
    print("Use responsibly and consider official APIs when available.")
    print("=" * 60)
    print()

    # Fetch per brand to increase precision
    sources = ["amazon", "chewy", "petco"] if args.source == "all" else [args.source]
    products: List[CatFoodProduct] = []
    for brand in preferred_brands or [""]:
        for src in sources:
            if src == "amazon":
                scraper = AmazonScraper(delay=args.delay)
            elif src == "chewy":
                scraper = ChewyScraper(delay=args.delay)
            elif src == "petco":
                scraper = PetcoScraper(delay=args.delay)
            else:
                raise ValueError(f"Unknown source: {src}")

            fetched = scraper.fetch(brand, args.type, args.count)
            for p in fetched:
                p.food_type = scraper.normalize_food_type(args.type)
            products.extend(fetched)
            print(f"Fetched {len(fetched)} products from {src} for brand query '{brand}'")

    if preferred_brands:
        products = [p for p in products if brand_matches(p, preferred_brands)]
        # Normalize brand field to canonical list
        for p in products:
            canonical = infer_canonical_brand(p.name, preferred_brands)
            if canonical:
                p.brand = canonical

    # Deduplicate
    seen: set[Tuple[str, str]] = set()
    deduped: List[CatFoodProduct] = []
    for p in products:
        key = ((p.name or "").strip().lower(), (p.url or "").strip().lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(p)
    products = deduped

    if not products:
        raise SystemExit("No products fetched; nothing to write/import.")

    output_path = Path(args.output).expanduser().resolve()
    save_to_csv(products, str(output_path))

    if args.skip_import:
        print("Skip import requested; done.")
        return

    if args.clear_existing:
        if not args.yes:
            raise SystemExit("Refusing to clear existing data without --yes.")
        await clear_cat_food_data()

    result = await import_csv_file(output_path)
    print(result.get("message", result))


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
