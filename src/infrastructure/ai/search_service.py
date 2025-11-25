from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import create_engine
from src.core.config import settings

class SearchService:
    def __init__(self):
        # We need a synchronous engine for LlamaIndex SQLDatabase
        # Construct sync URL from async URL or settings
        sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
        self.engine = create_engine(sync_db_url)
        self.sql_database = SQLDatabase(self.engine, include_tables=["cat_food_product", "ingredient"])
        
        # Text-to-SQL Engine
        self.sql_query_engine = NLSQLTableQueryEngine(
            sql_database=self.sql_database,
            tables=["cat_food_product", "ingredient"]
        )

    async def search(self, query: str) -> str:
        # Simple implementation: Use Text-to-SQL to query the DB based on natural language
        # For full hybrid (Vector + SQL), we would need to index the data in Qdrant first
        # and then use a RouterQueryEngine or similar.
        # For now, let's start with Text-to-SQL as requested for "structured filters".
        
        response = self.sql_query_engine.query(query)
        return str(response)
