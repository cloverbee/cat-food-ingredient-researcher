"""
Seed Data Generation Script for Cat Food Ingredient Researcher
This script generates realistic test data for products and ingredients.
"""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal, Base, engine
from src.domain.models.ingredient import Ingredient
from src.domain.models.product import CatFoodProduct

# Common cat food ingredients with descriptions and nutritional info
INGREDIENTS_DATA = [
    {
        "name": "Chicken",
        "description": "High-quality protein source from chicken meat. Essential for muscle development and maintenance.",
        "nutritional_value": {"protein": "18-20%", "fat": "15-20%", "calories_per_100g": 239},
        "common_allergens": ["poultry"],
    },
    {
        "name": "Chicken Meal",
        "description": "Concentrated source of chicken protein with most moisture removed. Higher protein content than fresh chicken.",
        "nutritional_value": {"protein": "65-70%", "fat": "12-18%", "calcium": "4%"},
        "common_allergens": ["poultry"],
    },
    {
        "name": "Turkey",
        "description": "Lean protein source from turkey meat. Good alternative for cats sensitive to chicken.",
        "nutritional_value": {"protein": "17-19%", "fat": "8-10%", "calories_per_100g": 189},
        "common_allergens": ["poultry"],
    },
    {
        "name": "Salmon",
        "description": "Rich in omega-3 fatty acids, particularly EPA and DHA. Supports healthy skin and coat.",
        "nutritional_value": {"protein": "20%", "fat": "13%", "omega_3": "2.2g", "omega_6": "1.5g"},
        "common_allergens": ["fish"],
    },
    {
        "name": "Tuna",
        "description": "High-protein fish source. Should be fed in moderation due to potential mercury content.",
        "nutritional_value": {"protein": "23%", "fat": "1%", "omega_3": "0.3g"},
        "common_allergens": ["fish"],
    },
    {
        "name": "Brown Rice",
        "description": "Whole grain carbohydrate source. Provides fiber and energy.",
        "nutritional_value": {"carbohydrates": "77%", "fiber": "3.5%", "protein": "7.5%"},
        "common_allergens": ["grain"],
    },
    {
        "name": "Sweet Potato",
        "description": "Easily digestible carbohydrate. Rich in vitamins A and C. Good for sensitive stomachs.",
        "nutritional_value": {
            "carbohydrates": "20%",
            "fiber": "3%",
            "vitamin_a": "14187 IU",
            "beta_carotene": "8509 mcg",
        },
        "common_allergens": [],
    },
    {
        "name": "Peas",
        "description": "Plant-based protein and fiber source. Gluten-free alternative to grains.",
        "nutritional_value": {"protein": "5%", "fiber": "5.7%", "carbohydrates": "14%"},
        "common_allergens": ["legume"],
    },
    {
        "name": "Beef",
        "description": "Rich protein source with high iron content. May cause allergies in some cats.",
        "nutritional_value": {"protein": "26%", "fat": "15%", "iron": "2.6mg", "zinc": "6mg"},
        "common_allergens": ["beef"],
    },
    {
        "name": "Lamb",
        "description": "Novel protein source often used in hypoallergenic diets.",
        "nutritional_value": {"protein": "25%", "fat": "21%", "vitamin_b12": "2.6mcg"},
        "common_allergens": ["lamb"],
    },
    {
        "name": "Duck",
        "description": "Alternative poultry protein. Often used in limited ingredient diets.",
        "nutritional_value": {"protein": "19%", "fat": "35%", "selenium": "14mcg"},
        "common_allergens": ["poultry"],
    },
    {
        "name": "Chicken Liver",
        "description": "Nutrient-dense organ meat. Excellent source of vitamins A and B12.",
        "nutritional_value": {"protein": "17%", "fat": "5%", "vitamin_a": "11078 IU", "vitamin_b12": "16.85mcg"},
        "common_allergens": ["poultry"],
    },
    {
        "name": "Fish Oil",
        "description": "Concentrated source of omega-3 fatty acids. Supports brain, heart, and joint health.",
        "nutritional_value": {"omega_3": "30%", "epa": "18%", "dha": "12%"},
        "common_allergens": ["fish"],
    },
    {
        "name": "Chicken Fat",
        "description": "High-quality fat source providing essential fatty acids and energy.",
        "nutritional_value": {"fat": "99%", "omega_6": "21%", "omega_3": "1%"},
        "common_allergens": ["poultry"],
    },
    {
        "name": "Carrots",
        "description": "Provides fiber and beta-carotene for eye health.",
        "nutritional_value": {"fiber": "2.8%", "vitamin_a": "16706 IU", "beta_carotene": "8285mcg"},
        "common_allergens": [],
    },
    {
        "name": "Blueberries",
        "description": "Antioxidant-rich fruit. Supports immune system and urinary tract health.",
        "nutritional_value": {"fiber": "2.4%", "vitamin_c": "9.7mg", "antioxidants": "high"},
        "common_allergens": [],
    },
    {
        "name": "Cranberries",
        "description": "Supports urinary tract health. Rich in antioxidants.",
        "nutritional_value": {"fiber": "4.6%", "vitamin_c": "13.3mg", "proanthocyanidins": "present"},
        "common_allergens": [],
    },
    {
        "name": "Pumpkin",
        "description": "Excellent for digestive health. High in fiber and moisture.",
        "nutritional_value": {"fiber": "3%", "vitamin_a": "8513 IU", "moisture": "94%"},
        "common_allergens": [],
    },
    {
        "name": "Taurine",
        "description": "Essential amino acid for cats. Critical for heart and eye health.",
        "nutritional_value": {"amino_acid": "taurine", "typical_supplement": "0.1-0.2%"},
        "common_allergens": [],
    },
    {
        "name": "Vitamin E",
        "description": "Antioxidant vitamin. Supports immune system and skin health.",
        "nutritional_value": {"vitamin_e": "varies", "typical_supplement": "100-200 IU/kg"},
        "common_allergens": [],
    },
    {
        "name": "Whitefish",
        "description": "Mild-flavored protein source. Good for cats with sensitivities.",
        "nutritional_value": {"protein": "19%", "fat": "1%", "omega_3": "0.2g"},
        "common_allergens": ["fish"],
    },
    {
        "name": "Egg",
        "description": "Complete protein source with all essential amino acids. Highly digestible.",
        "nutritional_value": {"protein": "13%", "fat": "11%", "choline": "251mg"},
        "common_allergens": ["egg"],
    },
    {
        "name": "Flaxseed",
        "description": "Plant-based omega-3 source. Provides fiber and supports coat health.",
        "nutritional_value": {"omega_3": "23%", "fiber": "27%", "protein": "18%"},
        "common_allergens": [],
    },
    {
        "name": "Kelp",
        "description": "Seaweed providing natural iodine and minerals. Supports thyroid health.",
        "nutritional_value": {"iodine": "150mcg", "minerals": "various", "fiber": "present"},
        "common_allergens": [],
    },
    {
        "name": "Probiotics",
        "description": "Beneficial bacteria supporting digestive health and immune system.",
        "nutritional_value": {"live_cultures": "present", "typical_cfu": "100M-1B per serving"},
        "common_allergens": [],
    },
]

# Product data with realistic formulations
PRODUCTS_DATA = [
    {
        "name": "Premium Chicken & Rice Formula",
        "brand": "Whisker Delight",
        "price": 29.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "High-quality dry food with real chicken as the first ingredient. Complete and balanced nutrition for adult cats.",
        "ingredients": ["Chicken", "Chicken Meal", "Brown Rice", "Chicken Fat", "Carrots", "Taurine", "Vitamin E"],
    },
    {
        "name": "Kitten Growth Formula",
        "brand": "Pawsome Nutrition",
        "price": 34.99,
        "age_group": "kitten",
        "food_type": "dry",
        "description": "Specially formulated for growing kittens. Extra protein and DHA for brain development.",
        "ingredients": [
            "Chicken",
            "Chicken Meal",
            "Salmon",
            "Egg",
            "Sweet Potato",
            "Fish Oil",
            "Taurine",
            "Probiotics",
        ],
    },
    {
        "name": "Senior Cat Care",
        "brand": "Golden Years Pet Food",
        "price": 32.99,
        "age_group": "senior",
        "food_type": "dry",
        "description": "Easy-to-digest formula for senior cats. Joint support with reduced calories.",
        "ingredients": ["Turkey", "Chicken Meal", "Sweet Potato", "Pumpkin", "Fish Oil", "Blueberries", "Taurine"],
    },
    {
        "name": "Salmon Feast in Gravy",
        "brand": "Ocean's Best",
        "price": 24.99,
        "age_group": "adult",
        "food_type": "wet",
        "description": "Wild-caught salmon in savory gravy. Grain-free recipe rich in omega-3s.",
        "ingredients": ["Salmon", "Fish Oil", "Sweet Potato", "Carrots", "Taurine", "Vitamin E"],
    },
    {
        "name": "Tuna & Whitefish Pate",
        "brand": "Ocean's Best",
        "price": 22.99,
        "age_group": "adult",
        "food_type": "wet",
        "description": "Smooth pate made with real tuna and whitefish. No grains or fillers.",
        "ingredients": ["Tuna", "Whitefish", "Chicken Liver", "Pumpkin", "Taurine"],
    },
    {
        "name": "Grain-Free Turkey & Duck",
        "brand": "Pure Protein",
        "price": 39.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "Limited ingredient diet with novel proteins. Ideal for sensitive stomachs.",
        "ingredients": ["Turkey", "Duck", "Peas", "Sweet Potato", "Flaxseed", "Probiotics", "Taurine"],
    },
    {
        "name": "Lamb & Brown Rice",
        "brand": "Whisker Delight",
        "price": 36.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "Novel protein formula with lamb. Great for cats with common food sensitivities.",
        "ingredients": ["Lamb", "Brown Rice", "Peas", "Carrots", "Flaxseed", "Kelp", "Taurine", "Vitamin E"],
    },
    {
        "name": "Beef & Liver Medley",
        "brand": "Carnivore's Choice",
        "price": 27.99,
        "age_group": "adult",
        "food_type": "wet",
        "description": "Rich beef with nutrient-dense liver. High protein formula for active cats.",
        "ingredients": ["Beef", "Chicken Liver", "Beef Liver", "Sweet Potato", "Cranberries", "Taurine"],
    },
    {
        "name": "Kitten Chicken Pate",
        "brand": "Little Paws",
        "price": 26.99,
        "age_group": "kitten",
        "food_type": "wet",
        "description": "Soft pate perfect for weaning kittens. Extra calories for growth.",
        "ingredients": ["Chicken", "Chicken Liver", "Egg", "Fish Oil", "Pumpkin", "Taurine", "Probiotics"],
    },
    {
        "name": "Indoor Cat Formula",
        "brand": "Home Life",
        "price": 31.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "Reduced calorie formula for indoor cats. Added fiber for hairball control.",
        "ingredients": ["Chicken", "Brown Rice", "Peas", "Pumpkin", "Flaxseed", "Cranberries", "Probiotics", "Taurine"],
    },
    {
        "name": "Weight Management Chicken",
        "brand": "Fit Feline",
        "price": 33.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "Low-fat formula for weight control. High protein maintains muscle mass.",
        "ingredients": ["Chicken", "Chicken Meal", "Peas", "Carrots", "Pumpkin", "Kelp", "Taurine"],
    },
    {
        "name": "Sensitive Stomach Turkey",
        "brand": "Gentle Digest",
        "price": 37.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "Limited ingredient diet for sensitive tummies. Added probiotics and prebiotics.",
        "ingredients": ["Turkey", "Sweet Potato", "Pumpkin", "Flaxseed", "Probiotics", "Taurine"],
    },
    {
        "name": "Chicken & Pumpkin Stew",
        "brand": "Harvest Kitchen",
        "price": 25.99,
        "age_group": "adult",
        "food_type": "wet",
        "description": "Hearty stew with chunks of chicken and vegetables. No artificial preservatives.",
        "ingredients": ["Chicken", "Chicken Liver", "Pumpkin", "Carrots", "Peas", "Blueberries", "Taurine"],
    },
    {
        "name": "Wild Salmon & Sweet Potato",
        "brand": "Nature's Table",
        "price": 42.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "Premium grain-free formula with wild-caught salmon. Supports skin and coat health.",
        "ingredients": [
            "Salmon",
            "Whitefish",
            "Sweet Potato",
            "Peas",
            "Fish Oil",
            "Blueberries",
            "Cranberries",
            "Taurine",
        ],
    },
    {
        "name": "Senior Turkey & Chicken",
        "brand": "Golden Years Pet Food",
        "price": 28.99,
        "age_group": "senior",
        "food_type": "wet",
        "description": "Soft texture for senior cats. Glucosamine for joint support.",
        "ingredients": ["Turkey", "Chicken", "Chicken Liver", "Pumpkin", "Sweet Potato", "Fish Oil", "Taurine"],
    },
    {
        "name": "Duck & Pea Grain-Free",
        "brand": "Pure Protein",
        "price": 44.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "Single protein source formula. Perfect for elimination diets.",
        "ingredients": ["Duck", "Peas", "Sweet Potato", "Flaxseed", "Taurine", "Vitamin E"],
    },
    {
        "name": "Chicken & Cranberry",
        "brand": "Urinary Health Plus",
        "price": 38.99,
        "age_group": "adult",
        "food_type": "dry",
        "description": "Formulated to support urinary tract health. Controlled mineral levels.",
        "ingredients": ["Chicken", "Chicken Meal", "Brown Rice", "Cranberries", "Pumpkin", "Fish Oil", "Taurine"],
    },
    {
        "name": "Multi-Fish Ocean Blend",
        "brand": "Ocean's Best",
        "price": 29.99,
        "age_group": "adult",
        "food_type": "wet",
        "description": "Variety of fish proteins in natural broth. High moisture content.",
        "ingredients": ["Tuna", "Salmon", "Whitefish", "Fish Oil", "Sweet Potato", "Kelp", "Taurine"],
    },
    {
        "name": "Chicken & Egg Breakfast",
        "brand": "Morning Feast",
        "price": 30.99,
        "age_group": "adult",
        "food_type": "wet",
        "description": "High-protein breakfast formula. Complete amino acid profile.",
        "ingredients": ["Chicken", "Egg", "Chicken Liver", "Pumpkin", "Carrots", "Taurine", "Probiotics"],
    },
    {
        "name": "Kitten Salmon & Rice",
        "brand": "Pawsome Nutrition",
        "price": 36.99,
        "age_group": "kitten",
        "food_type": "dry",
        "description": "Brain-boosting DHA from salmon. Complete nutrition for kittens up to 1 year.",
        "ingredients": [
            "Salmon",
            "Chicken Meal",
            "Brown Rice",
            "Egg",
            "Fish Oil",
            "Blueberries",
            "Taurine",
            "Probiotics",
        ],
    },
]


async def create_ingredients(session: AsyncSession):
    """Create ingredient records"""
    print("Creating ingredients...")
    ingredients = []

    for ing_data in INGREDIENTS_DATA:
        ingredient = Ingredient(
            name=ing_data["name"],
            description=ing_data["description"],
            nutritional_value=ing_data["nutritional_value"],
            common_allergens=ing_data["common_allergens"],
        )
        session.add(ingredient)
        ingredients.append(ingredient)

    await session.commit()
    print(f"✓ Created {len(ingredients)} ingredients")
    return ingredients


async def create_products(session: AsyncSession):
    """Create product records with ingredient relationships"""
    print("Creating products...")

    # First, get all ingredients from database
    from sqlalchemy import select

    result = await session.execute(select(Ingredient))
    all_ingredients = {ing.name: ing for ing in result.scalars().all()}

    products = []
    for prod_data in PRODUCTS_DATA:
        # Create full ingredient list text
        ingredient_names = prod_data["ingredients"]
        full_ingredient_list = ", ".join(ingredient_names)

        # Create product
        product = CatFoodProduct(
            name=prod_data["name"],
            brand=prod_data["brand"],
            price=prod_data["price"],
            age_group=prod_data["age_group"],
            food_type=prod_data["food_type"],
            description=prod_data["description"],
            full_ingredient_list=full_ingredient_list,
        )

        # Add ingredient relationships
        for ing_name in ingredient_names:
            if ing_name in all_ingredients:
                product.ingredients.append(all_ingredients[ing_name])

        session.add(product)
        products.append(product)

    await session.commit()
    print(f"✓ Created {len(products)} products")
    return products


async def seed_database():
    """Main function to seed the database"""
    print("\n" + "=" * 60)
    print("Starting Database Seed Process")
    print("=" * 60 + "\n")

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session and populate data
    async with AsyncSessionLocal() as session:
        try:
            # Check if data already exists
            from sqlalchemy import func, select

            result = await session.execute(select(func.count(Ingredient.id)))
            ingredient_count = result.scalar()

            result = await session.execute(select(func.count(CatFoodProduct.id)))
            product_count = result.scalar()

            if ingredient_count > 0 or product_count > 0:
                print(f"⚠️  Database already contains data:")
                print(f"   - {ingredient_count} ingredients")
                print(f"   - {product_count} products")
                print("\nTo reseed, please clear the database first.")
                return

            # Create seed data
            await create_ingredients(session)
            await create_products(session)

            print("\n" + "=" * 60)
            print("✅ Database seeding completed successfully!")
            print("=" * 60)
            print(f"\nSummary:")
            print(f"  - Ingredients: {len(INGREDIENTS_DATA)}")
            print(f"  - Products: {len(PRODUCTS_DATA)}")
            print(f"  - Age groups: kitten, adult, senior")
            print(f"  - Food types: wet, dry")
            print(f"  - Brands: {len(set(p['brand'] for p in PRODUCTS_DATA))}")
            print("\n")

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
