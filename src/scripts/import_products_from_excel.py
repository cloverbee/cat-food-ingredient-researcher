"""
Import products from Excel file into the database.

This script reads an Excel file and creates new products in the database.
It converts the Excel data to CSV format and uses the ingestion service.

Expected Excel columns:
- name: Product name (required)
- brand: Brand name (optional, will try to extract from name if missing)
- price: Price (optional)
- ingredients: Ingredient list (optional)
- details: Description/details (optional)
- age_group: Age group (optional)
- food_type: Food type - Wet/Dry/Dessert (optional)
- image_url: Image URL (optional)
- shopping_url: Shopping URL (optional)

Usage:
  python -m src.scripts.import_products_from_excel --excel "cat food data.xlsx"
"""

import argparse
import asyncio
import csv
import io
from pathlib import Path

import pandas as pd

from src.core.database import AsyncSessionLocal
from src.domain.repositories.ingredient_repository import IngredientRepository
from src.domain.repositories.product_repository import ProductRepository
from src.domain.services.ingestion_service import IngestionService
from src.domain.services.ingredient_service import IngredientService
from src.domain.services.product_service import ProductService


def extract_brand_from_name(name: str) -> str:
    """Extract brand name from product name (first word or common brand patterns)."""
    if not name:
        return "Unknown"

    # Common brand patterns
    brand_patterns = [
        "Wysong",
        "Primal",
        "ZIWI Peak",
        "ZiwiPeak",
        "Dr. Elsey's",
        "Dr Elsey's",
        "Go!",
        "Farmina",
        "Fromm",
        "The Honest Kitchen",
        "Catit Gold Fern",
        "Only Natural Pet",
        "Instinct",
        "Wellness",
        "Addiction",
        "Nulo",
        "Life's Abundance",
        "Tiki Cat",
        "I And Love And You",
        "Essence",
        "Feline Natural",
        "Almo Nature",
        "Fussie Cat",
        "American Journey",
        "Bff",
        "Cats In The Kitchen",
        "Stella & Chewys",
        "Hound & Gatos",
    ]

    name_lower = name.lower()
    for brand in brand_patterns:
        if brand.lower() in name_lower:
            return brand

    # Fallback: use first word or first few words
    words = name.split()
    if words:
        # If first word is "The", include it
        if words[0].lower() == "the" and len(words) > 1:
            return f"{words[0]} {words[1]}"
        return words[0]

    return "Unknown"


def normalize_food_type(food_type: str) -> str:
    """Normalize food type to standard values."""
    if not food_type:
        return None

    food_type_lower = str(food_type).lower().strip()
    if "wet" in food_type_lower or "canned" in food_type_lower or "pouch" in food_type_lower:
        return "Wet"
    elif "dry" in food_type_lower or "kibble" in food_type_lower:
        return "Dry"
    elif "dessert" in food_type_lower or "treat" in food_type_lower:
        return "Dessert"
    elif "freeze" in food_type_lower or "air-dried" in food_type_lower or "dehydrated" in food_type_lower:
        return "Dry"  # Freeze-dried and air-dried are typically dry food
    else:
        return None


def infer_food_type_from_name(name: str) -> str:
    """Try to infer food type from product name."""
    if not name:
        return None

    name_lower = name.lower()

    # Check for wet food indicators
    if any(word in name_lower for word in ["wet", "canned", "pouch", "pate", "gravy", "broth", "stew"]):
        return "Wet"

    # Check for dry food indicators
    if any(word in name_lower for word in ["dry", "kibble", "freeze-dried", "air-dried", "dehydrated"]):
        return "Dry"

    # Check for treat/dessert indicators
    if any(word in name_lower for word in ["treat", "dessert", "snack"]):
        return "Dessert"

    return None


def excel_to_csv_string(df: pd.DataFrame) -> str:
    """Convert Excel DataFrame to CSV string format expected by ingestion service."""
    output = io.StringIO()

    # Map Excel columns to CSV columns
    csv_columns = [
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

    writer = csv.DictWriter(output, fieldnames=csv_columns)
    writer.writeheader()

    # Find Excel columns (case-insensitive, flexible matching)
    name_col = None
    brand_col = None
    price_col = None
    ingredients_col = None
    details_col = None
    age_group_col = None
    food_type_col = None
    image_url_col = None
    shopping_url_col = None

    for col in df.columns:
        col_lower = col.lower().strip()
        if "name" in col_lower and name_col is None:
            name_col = col
        elif "brand" in col_lower and brand_col is None:
            brand_col = col
        elif "price" in col_lower and price_col is None:
            price_col = col
        elif "ingredient" in col_lower and ingredients_col is None:
            ingredients_col = col
        elif "detail" in col_lower or "description" in col_lower and details_col is None:
            details_col = col
        elif "age" in col_lower and age_group_col is None:
            age_group_col = col
        elif "food_type" in col_lower or "type" in col_lower and food_type_col is None:
            food_type_col = col
        elif "image" in col_lower and image_url_col is None:
            image_url_col = col
        elif "shopping" in col_lower or "url" in col_lower and shopping_url_col is None:
            shopping_url_col = col

    if name_col is None:
        raise ValueError(f"Could not find a 'name' column in the Excel file. Available columns: {df.columns.tolist()}")

    print("Using columns:")
    print(f"  Name: {name_col}")
    if brand_col:
        print(f"  Brand: {brand_col}")
    if price_col:
        print(f"  Price: {price_col}")
    if ingredients_col:
        print(f"  Ingredients: {ingredients_col}")
    if details_col:
        print(f"  Details/Description: {details_col}")
    if age_group_col:
        print(f"  Age Group: {age_group_col}")
    if food_type_col:
        print(f"  Food Type: {food_type_col}")
    if image_url_col:
        print(f"  Image URL: {image_url_col}")
    if shopping_url_col:
        print(f"  Shopping URL: {shopping_url_col}")

    # Process each row
    for _idx, row in df.iterrows():
        name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
        if not name:
            continue

        # Extract brand
        if brand_col and pd.notna(row[brand_col]):
            brand = str(row[brand_col]).strip()
        else:
            brand = extract_brand_from_name(name)

        # Extract price
        price = None
        if price_col and pd.notna(row[price_col]):
            try:
                price_val = row[price_col]
                if isinstance(price_val, str):
                    price = float(price_val.replace("$", "").replace(",", "").strip())
                else:
                    price = float(price_val)
            except (ValueError, TypeError):
                price = None

        # Extract ingredients
        ingredients = None
        if ingredients_col and pd.notna(row[ingredients_col]):
            ingredients_str = str(row[ingredients_col]).strip()
            # Clean up ingredients - ensure comma-separated
            if "," in ingredients_str:
                ingredients = ", ".join([i.strip() for i in ingredients_str.split(",") if i.strip()])
            elif ";" in ingredients_str:
                ingredients = ", ".join([i.strip() for i in ingredients_str.split(";") if i.strip()])
            elif "\n" in ingredients_str:
                ingredients = ", ".join([i.strip() for i in ingredients_str.split("\n") if i.strip()])
            else:
                ingredients = ingredients_str

        # Extract description
        description = None
        if details_col and pd.notna(row[details_col]):
            description = str(row[details_col]).strip()

        # Extract age group
        age_group = None
        if age_group_col and pd.notna(row[age_group_col]):
            age_group = str(row[age_group_col]).strip()

        # Extract food type
        food_type = None
        if food_type_col and pd.notna(row[food_type_col]):
            food_type = normalize_food_type(str(row[food_type_col]))
        else:
            # Try to infer from name
            food_type = infer_food_type_from_name(name)

        # Extract image URL
        image_url = None
        if image_url_col and pd.notna(row[image_url_col]):
            image_url = str(row[image_url_col]).strip()

        # Extract shopping URL
        shopping_url = None
        if shopping_url_col and pd.notna(row[shopping_url_col]):
            shopping_url = str(row[shopping_url_col]).strip()

        # Write CSV row
        writer.writerow(
            {
                "name": name,
                "brand": brand,
                "price": price or "",
                "age_group": age_group or "",
                "food_type": food_type or "",
                "description": description or "",
                "full_ingredient_list": ingredients or "",
                "image_url": image_url or "",
                "shopping_url": shopping_url or "",
            }
        )

    return output.getvalue()


async def import_from_excel(excel_path: Path) -> dict:
    """Import products from Excel file."""
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)

    print(f"Found {len(df)} rows in Excel file")
    print(f"Columns: {df.columns.tolist()}")

    # Convert to CSV format
    csv_content = excel_to_csv_string(df)

    # Import using ingestion service
    async with AsyncSessionLocal() as db:
        product_repo = ProductRepository(db)
        ingredient_repo = IngredientRepository(db)
        product_service = ProductService(product_repo)
        ingredient_service = IngredientService(ingredient_repo)
        ingestion_service = IngestionService(product_service, ingredient_service)

        result = await ingestion_service.ingest_csv_content(csv_content)

        return result


async def main_async():
    """Main async function."""
    parser = argparse.ArgumentParser(description="Import cat food products from Excel file")
    parser.add_argument("--excel", required=True, help="Path to Excel file with product data")
    args = parser.parse_args()

    excel_path = Path(args.excel).expanduser().resolve()
    if not excel_path.exists():
        raise SystemExit(f"Excel file not found: {excel_path}")

    print("=" * 70)
    print("Import Products from Excel")
    print("=" * 70)

    result = await import_from_excel(excel_path)

    print("\n" + "=" * 70)
    print("Import Summary:")
    # The ingestion service returns a message string, parse it or show the message
    if isinstance(result, dict):
        message = result.get("message", str(result))
        print(f"  {message}")
        # Try to extract numbers from message if possible
        if "products_created" in result:
            print(f"  Products created: {result.get('products_created', 0)}")
        if "ingredients_created" in result:
            print(f"  Ingredients created: {result.get('ingredients_created', 0)}")
        if "errors" in result:
            print(f"  Errors: {len(result.get('errors', []))}")
            for error in result.get("errors", [])[:5]:  # Show first 5 errors
                print(f"    - {error}")
    else:
        print(f"  Result: {result}")
    print("=" * 70)


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
