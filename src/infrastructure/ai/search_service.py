import re

from llama_index.core import Settings, SQLDatabase, VectorStoreIndex
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import create_engine, text

from src.core.config import settings


class SearchService:
    def __init__(self):
        # We need a synchronous engine for LlamaIndex SQLDatabase
        # Construct sync URL from async URL or settings
        sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
        self.engine = create_engine(sync_db_url, echo=True)  # Enable SQL logging
        self.sql_database = SQLDatabase(self.engine, include_tables=["cat_food_product", "ingredient"])

        # Create schema context to help the LLM understand the data better
        context_str = """
        Database Schema Information:

        Table: cat_food_product
        - id: integer (primary key)
        - name: string (product name)
        - brand: string (brand name)
        - price: float (price in dollars)
        - age_group: string (target age group - examples: 'Kitten', 'Adult', 'Senior', 'Kitten (1-12m)', 'Adult (1-7y)', 'Senior (7+y)')
        - food_type: string (type of food - values: 'Wet', 'Dry', 'Snack')
        - description: text (product description)
        - full_ingredient_list: text (comma-separated ingredients)

        CRITICAL RULES FOR SQL GENERATION:

        1. NEVER use exact equality (=) for age_group because it contains additional info in parentheses.
           WRONG: WHERE age_group = 'Kitten'
           CORRECT: WHERE age_group ILIKE '%kitten%'

        2. ALWAYS use ILIKE with wildcards for age_group:
           - Kittens: WHERE age_group ILIKE '%kitten%'
           - Adults: WHERE age_group ILIKE '%adult%'
           - Seniors: WHERE age_group ILIKE '%senior%'

        3. For food_type, use ILIKE for case-insensitive matching:
           - Wet food: WHERE food_type ILIKE '%wet%'
           - Dry food: WHERE food_type ILIKE '%dry%'

        CORRECT Example Queries:
        - "Find wet food for kittens":
          SELECT * FROM cat_food_product WHERE food_type ILIKE '%wet%' AND age_group ILIKE '%kitten%';

        - "Find adult dry food":
          SELECT * FROM cat_food_product WHERE food_type ILIKE '%dry%' AND age_group ILIKE '%adult%';

        - "Show me kitten food":
          SELECT * FROM cat_food_product WHERE age_group ILIKE '%kitten%';

        - "Wet food products":
          SELECT * FROM cat_food_product WHERE food_type ILIKE '%wet%';
        """

        # Text-to-SQL Engine with enhanced context
        self.sql_query_engine = NLSQLTableQueryEngine(
            sql_database=self.sql_database,
            tables=["cat_food_product", "ingredient"],
            context_str_prefix=context_str,
            verbose=True,  # Enable verbose logging to see generated SQL
            synthesize_response=True,
        )

    def _extract_search_params(self, query: str) -> dict:
        """Extract search parameters using LLM"""
        prompt = f"""
        Extract search parameters from this query: "{query}"

        Return ONLY a valid JSON object with these fields (use null if not mentioned):
        {{
            "food_type": "wet" or "dry" or "snack" or null,
            "age_group": "kitten" or "adult" or "senior" or null,
            "brand": "brand name" or null,
            "max_price": number or null
        }}

        Example: "Find wet food for kittens" should return: {{"food_type": "wet", "age_group": "kitten", "brand": null, "max_price": null}}
        """

        import json

        response = Settings.llm.complete(prompt)
        try:
            # Extract JSON from response
            text = str(response)
            # Find JSON object in the response
            json_match = re.search(r"\{[^}]+\}", text)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except:
            return {}

    def _build_sql_query(self, params: dict) -> str:
        """Build SQL query from extracted parameters"""
        conditions = []

        if params.get("food_type"):
            conditions.append(f"food_type ILIKE '%{params['food_type']}%'")

        if params.get("age_group"):
            conditions.append(f"age_group ILIKE '%{params['age_group']}%'")

        if params.get("brand"):
            conditions.append(f"brand ILIKE '%{params['brand']}%'")

        if params.get("max_price"):
            conditions.append(f"price <= {params['max_price']}")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
        SELECT id, name, brand, price, food_type, age_group, description
        FROM cat_food_product
        WHERE {where_clause}
        ORDER BY name
        LIMIT 20;
        """

        return sql

    async def search(self, query: str) -> str:
        # Extract search parameters from natural language
        params = self._extract_search_params(query)
        print(f"Extracted params: {params}")

        # Build SQL query programmatically
        sql = self._build_sql_query(params)
        print(f"Generated SQL: {sql}")

        # Execute the query
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()

        if not rows:
            return "No products found matching your criteria."

        # Format results
        response_lines = [f"Found {len(rows)} product(s):\n"]
        for row in rows:
            response_lines.append(
                f"- {row.name} by {row.brand} (${row.price}) - {row.food_type} food for {row.age_group}"
            )

        return "\n".join(response_lines)
