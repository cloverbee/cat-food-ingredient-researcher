import csv
import io
from typing import Dict, List

from src.domain.schemas.product import ProductCreate, ProductRead
from src.domain.services.ingredient_service import IngredientService
from src.domain.services.product_service import ProductService


class IngestionService:
    def __init__(self, product_service: ProductService, ingredient_service: IngredientService):
        self.product_service = product_service
        self.ingredient_service = ingredient_service

    def parse_ingredient_list(self, raw_ingredients: str) -> List[str]:
        """Parse comma-separated ingredient string into a list of ingredient names."""
        if not raw_ingredients:
            return []
        return [name.strip() for name in raw_ingredients.split(",") if name.strip()]

    async def ingest_product_from_row(self, row: Dict[str, str]) -> ProductRead:
        """Process a single CSV row and create a product with linked ingredients."""
        # Parse ingredients if available
        ingredient_ids = []
        raw_ingredients = row.get("full_ingredient_list")

        if raw_ingredients:
            ingredient_names = self.parse_ingredient_list(raw_ingredients)
            if ingredient_names:
                ingredients = await self.ingredient_service.get_or_create_ingredients(ingredient_names)
                ingredient_ids = [ing.id for ing in ingredients]

        # Create Product
        product_data = ProductCreate(
            name=row.get("name"),
            brand=row.get("brand"),
            price=float(row.get("price", 0)),
            age_group=row.get("age_group"),
            food_type=row.get("food_type"),
            description=row.get("description"),
            full_ingredient_list=raw_ingredients,
            ingredient_ids=ingredient_ids,
        )

        return await self.product_service.create_product(product_data)

    async def ingest_csv_content(self, csv_content: str) -> Dict[str, str]:
        """Process entire CSV content and return ingestion summary."""
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        products_created = 0

        for row in csv_reader:
            try:
                await self.ingest_product_from_row(row)
                products_created += 1
            except Exception as e:
                print(f"Error processing row {row}: {e}")
                continue

        return {"message": f"Successfully ingested {products_created} products."}
