"""
Generate mock cat food product data for testing.

This script generates realistic mock data when real data fetching is not available.
Useful for testing and development.

Usage:
    python -m src.scripts.generate_mock_cat_food_data --type dry --count 100
"""

import argparse
import csv
import random
from typing import List

# Popular cat food brands
BRANDS = [
    "Purina",
    "Whiskas",
    "Fancy Feast",
    "Friskies",
    "Iams",
    "Hill's Science Diet",
    "Royal Canin",
    "Blue Buffalo",
    "Wellness",
    "Merrick",
    "Orijen",
    "Acana",
    "Taste of the Wild",
    "Nutro",
    "Natural Balance",
    "Fromm",
    "Instinct",
    "Ziwi Peak",
    "Tiki Cat",
    "Weruva",
]

# Product name templates by type
DRY_FOOD_NAMES = [
    "Complete Nutrition",
    "Indoor Formula",
    "Adult Formula",
    "Kitten Formula",
    "Senior Formula",
    "Weight Management",
    "Hairball Control",
    "Sensitive Stomach",
    "Grain-Free",
    "Natural Recipe",
    "Premium Blend",
    "Original Recipe",
    "Chicken & Rice",
    "Salmon & Rice",
    "Turkey & Rice",
    "Ocean Fish",
    "Indoor Cat",
    "Healthy Weight",
    "Urinary Health",
    "Digestive Health",
]

WET_FOOD_NAMES = [
    "Pate",
    "Gravy",
    "Sliced",
    "Flaked",
    "Shredded",
    "Chunks in Gravy",
    "Sliced in Gravy",
    "Pate Variety Pack",
    "Gourmet",
    "Classic",
    "Tender",
    "Savory",
    "Delights",
    "Feast",
    "Favorites",
    "Select",
    "Premium",
    "Natural",
    "Complete",
    "Entree",
]

DESSERT_NAMES = [
    "Cat Treats",
    "Crunchy Treats",
    "Soft Treats",
    "Dental Treats",
    "Training Treats",
    "Freeze-Dried",
    "Catnip Treats",
    "Salmon Treats",
    "Chicken Treats",
    "Tuna Treats",
    "Gourmet Treats",
    "Natural Treats",
    "Healthy Treats",
    "Yummy Treats",
    "Tempting Treats",
]

# Age groups
AGE_GROUPS = ["Kitten", "Adult", "Senior", None]

# Common ingredients
INGREDIENTS = [
    "Chicken",
    "Chicken Meal",
    "Turkey",
    "Salmon",
    "Tuna",
    "Whitefish",
    "Brown Rice",
    "Brewers Rice",
    "Corn Gluten Meal",
    "Wheat",
    "Soybean Meal",
    "Chicken Fat",
    "Fish Oil",
    "Flaxseed",
    "Pea Protein",
    "Potato",
    "Sweet Potato",
    "Carrots",
    "Peas",
    "Cranberries",
    "Blueberries",
    "Taurine",
    "Vitamins",
    "Minerals",
    "Natural Flavors",
    "Preservatives",
]


def generate_product_name(brand: str, food_type: str) -> str:
    """Generate a product name."""
    if food_type.lower() == "dry":
        template = random.choice(DRY_FOOD_NAMES)
    elif food_type.lower() == "wet":
        template = random.choice(WET_FOOD_NAMES)
    else:  # dessert
        template = random.choice(DESSERT_NAMES)

    return f"{brand} {template}"


def generate_ingredients() -> str:
    """Generate a random ingredient list."""
    num_ingredients = random.randint(5, 12)
    selected = random.sample(INGREDIENTS, num_ingredients)
    return ", ".join(selected)


def generate_price(food_type: str) -> float:
    """Generate a realistic price."""
    if food_type.lower() == "dry":
        return round(random.uniform(8.99, 45.99), 2)
    elif food_type.lower() == "wet":
        return round(random.uniform(12.99, 35.99), 2)
    else:  # dessert
        return round(random.uniform(3.99, 15.99), 2)


def generate_description(brand: str, name: str, food_type: str) -> str:
    """Generate a product description."""
    descriptions = [
        f"Premium {food_type.lower()} cat food formulated for optimal nutrition.",
        "Complete and balanced nutrition for cats of all life stages.",
        f"Made with real {random.choice(['chicken', 'salmon', 'turkey'])} as the first ingredient.",
        f"Natural {food_type.lower()} food with no artificial preservatives.",
        "Specially formulated to support your cat's health and wellbeing.",
    ]
    return random.choice(descriptions)


def generate_products(food_type: str, count: int) -> List[dict]:
    """Generate mock cat food products."""
    products = []

    for _ in range(count):
        brand = random.choice(BRANDS)
        name = generate_product_name(brand, food_type)
        age_group = random.choice(AGE_GROUPS)

        product = {
            "name": name,
            "brand": brand,
            "price": generate_price(food_type),
            "age_group": age_group if age_group else "",
            "food_type": food_type.capitalize(),
            "description": generate_description(brand, name, food_type),
            "full_ingredient_list": generate_ingredients(),
        }

        products.append(product)

    return products


def save_to_csv(products: List[dict], filename: str):
    """Save products to CSV file."""
    if not products:
        print("No products to save")
        return

    fieldnames = ["name", "brand", "price", "age_group", "food_type", "description", "full_ingredient_list"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)

    print(f"✅ Generated {len(products)} mock products and saved to {filename}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate mock cat food product data")
    parser.add_argument("--type", choices=["dry", "wet", "dessert"], required=True, help="Food type")
    parser.add_argument("--count", type=int, default=100, help="Number of products to generate")
    parser.add_argument("--output", default=None, help="Output CSV filename (default: cat_food_{type}_mock.csv)")

    args = parser.parse_args()

    if args.output is None:
        args.output = f"cat_food_{args.type}_mock.csv"

    print(f"Generating {args.count} mock {args.type} food products...")
    products = generate_products(args.type, args.count)
    save_to_csv(products, args.output)


if __name__ == "__main__":
    main()
