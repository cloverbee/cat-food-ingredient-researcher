"""
Rainforest API Fetcher for Cat Food Products

This script uses the Rainforest API to fetch cat food product data from Amazon
without requiring an Amazon Associates account or sales history.

Setup:
1. Sign up at https://www.rainforestapi.com/ (free tier: 100 requests/month)
2. Get your API key from the dashboard
3. Set environment variable: RAINFOREST_API_KEY=your_api_key

Usage:
    python -m src.scripts.rainforest_api_fetcher --count 100
    python -m src.scripts.rainforest_api_fetcher --type dry --count 30
"""

import argparse
import csv
import os
import time
from pathlib import Path
from typing import List, Optional

import requests

# Handle dotenv import
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore

# Load .env file if it exists
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists() and load_dotenv:
    try:
        load_dotenv(env_path)
    except Exception as e:
        print(f"⚠️  Warning: Could not load .env file: {e}")


# Rainforest API base URL
RAINFOREST_API_URL = "https://api.rainforestapi.com/request"


def get_api_key() -> str:
    """Get Rainforest API key from environment."""
    api_key = os.getenv("RAINFOREST_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing Rainforest API key. Set RAINFOREST_API_KEY environment variable.\n"
            "Sign up for free at: https://www.rainforestapi.com/"
        )
    return api_key


def search_products(api_key: str, query: str, page: int = 1) -> dict:
    """Search for products using Rainforest API."""
    params = {
        "api_key": api_key,
        "type": "search",
        "amazon_domain": "amazon.com",
        "search_term": query,
        "page": page,
        "category_id": "2975312011",  # Cat Food category on Amazon
    }

    try:
        response = requests.get(RAINFOREST_API_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return {}


def extract_product_data(item: dict, food_type: str) -> dict:
    """Extract relevant product data from API response item."""
    name = item.get("title", "Unknown")

    # Extract brand from title or brand field
    brand = "Unknown"
    if "brand" in item:
        brand = item["brand"]
    elif "," in name:
        # Often brand is the first part of the title
        brand = name.split(",")[0].strip()

    # Get price
    price = None
    if "price" in item and item["price"]:
        price_data = item["price"]
        if isinstance(price_data, dict):
            price = price_data.get("value")
        elif isinstance(price_data, (int, float)):
            price = price_data

    # Get image URL
    image_url = item.get("image")

    # Get shopping URL (Amazon link)
    shopping_url = item.get("link")

    # Detect age group from title
    age_group = None
    title_lower = name.lower()
    if "kitten" in title_lower or "young" in title_lower:
        age_group = "Kitten"
    elif "senior" in title_lower or "mature" in title_lower or "7+" in title_lower:
        age_group = "Senior"
    elif "adult" in title_lower:
        age_group = "Adult"

    return {
        "name": name,
        "brand": brand,
        "price": price,
        "age_group": age_group,
        "food_type": food_type.capitalize(),
        "description": None,  # Not always available in search results
        "full_ingredient_list": None,  # Would need product detail request
        "image_url": image_url,
        "shopping_url": shopping_url,
    }


def fetch_cat_food(
    api_key: str,
    food_type: Optional[str] = None,
    count: int = 100,
) -> List[dict]:
    """Fetch cat food products from Amazon via Rainforest API."""
    products = []
    seen_urls = set()  # Track URLs to avoid duplicates

    # Define search queries based on food type
    if food_type == "dry":
        queries = ["cat dry food kibble", "dry cat food"]
    elif food_type == "wet":
        queries = ["cat wet food canned", "wet cat food pate"]
    elif food_type == "dessert":
        queries = ["cat treats snacks", "cat dessert treats"]
    else:
        # Fetch a mix of all types
        queries = [
            "cat dry food",
            "cat wet food",
            "cat treats",
        ]

    products_per_query = count // len(queries) + 1
    current_food_type = food_type or "mixed"

    for _query_idx, query in enumerate(queries):
        if len(products) >= count:
            break

        # Update food type for mixed queries
        if not food_type:
            if "dry" in query:
                current_food_type = "dry"
            elif "wet" in query:
                current_food_type = "wet"
            else:
                current_food_type = "dessert"

        page = 1
        query_products = 0

        print(f"\n🔍 Searching: '{query}'")

        while query_products < products_per_query and len(products) < count:
            print(f"  Fetching page {page}...")

            result = search_products(api_key, query, page)

            if not result:
                print(f"  ⚠️ No results returned for page {page}")
                break

            # Check for API errors
            if "request_info" in result and not result["request_info"].get("success", True):
                error_msg = result["request_info"].get("message", "Unknown error")
                print(f"  ❌ API Error: {error_msg}")
                break

            search_results = result.get("search_results", [])

            if not search_results:
                print("  No more products found")
                break

            new_count = 0
            for item in search_results:
                if len(products) >= count:
                    break

                # Skip duplicates
                url = item.get("link", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                product = extract_product_data(item, current_food_type)
                products.append(product)
                query_products += 1
                new_count += 1

            print(f"  Added {new_count} products (Total: {len(products)})")

            # Check if there are more pages
            pagination = result.get("pagination", {})
            if not pagination.get("has_next_page", False):
                break

            page += 1

            # Rate limiting - be nice to the API
            time.sleep(1)

    return products[:count]


def save_to_csv(products: List[dict], filename: str):
    """Save products to CSV file."""
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

    print(f"\n✅ Saved {len(products)} products to {filename}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Fetch cat food products from Amazon via Rainforest API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 100 mixed cat food products
  python -m src.scripts.rainforest_api_fetcher --count 100

  # Fetch 30 dry food products
  python -m src.scripts.rainforest_api_fetcher --type dry --count 30

  # Fetch 50 wet food products with custom output
  python -m src.scripts.rainforest_api_fetcher --type wet --count 50 --output wet_food.csv

Setup:
  1. Sign up at https://www.rainforestapi.com/ (free tier: 100 requests/month)
  2. Get your API key from the dashboard
  3. Set environment variable or add to .env file:
     RAINFOREST_API_KEY=your_api_key
        """,
    )
    parser.add_argument(
        "--type",
        choices=["dry", "wet", "dessert"],
        default=None,
        help="Food type (dry/wet/dessert). If not specified, fetches a mix of all types.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of products to fetch (default: 100)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV filename (default: cat_food_rainforest.csv or cat_food_{type}_rainforest.csv)",
    )

    args = parser.parse_args()

    # Set default output filename
    if args.output is None:
        if args.type:
            args.output = f"cat_food_{args.type}_rainforest.csv"
        else:
            args.output = "cat_food_rainforest.csv"

    # Get API key
    try:
        api_key = get_api_key()
    except ValueError as e:
        print(f"❌ {e}")
        print("\n📝 Setup Instructions:")
        print("=" * 60)
        print("1. Sign up at https://www.rainforestapi.com/")
        print("   (Free tier: 100 requests/month)")
        print("\n2. Get your API key from the dashboard")
        print("\n3. Set environment variable:")
        print("   export RAINFOREST_API_KEY='your_api_key'")  # pragma: allowlist secret
        print("\n   OR add to .env file in project root:")
        print("   RAINFOREST_API_KEY=your_api_key")
        print("=" * 60)
        return

    print("=" * 60)
    print("Rainforest API - Cat Food Fetcher")
    print("=" * 60)
    print(f"Food Type: {args.type or 'All (mixed)'}")
    print(f"Target Count: {args.count}")
    print(f"Output File: {args.output}")
    print("=" * 60)

    products = fetch_cat_food(api_key, args.type, args.count)

    if products:
        save_to_csv(products, args.output)
        print(f"\n🎉 Successfully fetched {len(products)} cat food products!")
        print(f"📁 Saved to: {args.output}")
    else:
        print("\n❌ No products found")
        print("\nTroubleshooting:")
        print("- Check your API key is correct")
        print("- Verify you haven't exceeded your monthly limit")
        print("- Try again in a few minutes")


if __name__ == "__main__":
    main()
