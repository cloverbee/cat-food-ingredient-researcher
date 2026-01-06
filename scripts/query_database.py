#!/usr/bin/env python3
"""
Simple database query script.
Run custom queries against your database.
"""
import asyncio
import sys
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings


async def run_query(query: str, limit: Optional[int] = None):
    """Run a SQL query and display results."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    try:
        async with engine.connect() as conn:
            # Add LIMIT if not present and limit is specified
            if limit and "LIMIT" not in query.upper():
                query = f"{query.rstrip(';')} LIMIT {limit}"

            print("=" * 80)
            print("QUERY:")
            print("=" * 80)
            print(query)
            print()
            print("=" * 80)
            print("RESULTS:")
            print("=" * 80)

            result = await conn.execute(text(query))
            rows = result.fetchall()
            column_names = [desc[0] for desc in result.description]

            if not rows:
                print("No rows returned.")
                return

            # Print column headers
            header = " | ".join(f"{name[:20]:<20}" for name in column_names)
            print(header)
            print("-" * len(header))

            # Print rows
            for row in rows:
                row_str = " | ".join(f"{str(val)[:20]:<20}" if val is not None else f"{'NULL':<20}" for val in row)
                print(row_str)

            print()
            print(f"Total rows: {len(rows)}")

    except Exception as e:
        print(f"Error executing query: {e}")
        raise
    finally:
        await engine.dispose()


async def show_tables():
    """Show all tables and row counts."""
    query = """
        SELECT
            table_name,
            (SELECT COUNT(*) FROM information_schema.columns
             WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    await run_query(query)


async def count_rows():
    """Count rows in all tables."""
    tables = ["cat_food_product", "ingredient", "product_ingredient_association"]

    for table in tables:
        query = f'SELECT COUNT(*) as row_count FROM "{table}"'
        print(f"\n{table}:")
        await run_query(query, limit=None)


async def show_sample_products(limit: int = 5):
    """Show sample products."""
    query = """
        SELECT id, name, brand, price, age_group, food_type
        FROM cat_food_product
        ORDER BY id
    """
    await run_query(query, limit=limit)


async def show_sample_ingredients(limit: int = 5):
    """Show sample ingredients."""
    query = """
        SELECT id, name, description
        FROM ingredient
        ORDER BY id
    """
    await run_query(query, limit=limit)


async def show_products_with_ingredients(limit: int = 10):
    """Show products with their ingredients."""
    query = """
        SELECT
            p.id as product_id,
            p.name AS product_name,
            p.brand,
            i.name AS ingredient_name
        FROM cat_food_product p
        JOIN product_ingredient_association pia ON p.id = pia.product_id
        JOIN ingredient i ON pia.ingredient_id = i.id
        ORDER BY p.id, i.name
    """
    await run_query(query, limit=limit)


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/query_database.py <command> [options]")
        print()
        print("Commands:")
        print("  tables              - Show all tables")
        print("  count               - Count rows in all tables")
        print("  products [limit]    - Show sample products (default: 5)")
        print("  ingredients [limit] - Show sample ingredients (default: 5)")
        print("  relationships [limit] - Show products with ingredients (default: 10)")
        print("  query '<SQL>'       - Run custom SQL query")
        print()
        print("Examples:")
        print("  python3 scripts/query_database.py tables")
        print("  python3 scripts/query_database.py products 10")
        print("  python3 scripts/query_database.py query \"SELECT * FROM cat_food_product WHERE brand = 'Purina'\"")
        return

    command = sys.argv[1].lower()

    try:
        if command == "tables":
            await show_tables()
        elif command == "count":
            await count_rows()
        elif command == "products":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            await show_sample_products(limit)
        elif command == "ingredients":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            await show_sample_ingredients(limit)
        elif command == "relationships":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            await show_products_with_ingredients(limit)
        elif command == "query":
            if len(sys.argv) < 3:
                print("Error: Please provide a SQL query in quotes")
                return
            query = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
            await run_query(query, limit)
        else:
            print(f"Unknown command: {command}")
            print("Run without arguments to see usage.")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
