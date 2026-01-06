#!/usr/bin/env python3
"""
Database inspection script.
Shows table names, column information, row counts, and sample data.
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add project root to path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import settings


async def inspect_database(show_sample_data: bool = True, limit: int = 5):
    """Inspect database schema and optionally show sample data."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    try:
        async with engine.connect() as conn:
            print("=" * 80)
            print("DATABASE INSPECTION")
            print("=" * 80)
            print(f"Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'hidden'}")
            print()

            # Get all table names
            result = await conn.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """
                )
            )
            tables = [row[0] for row in result.fetchall()]

            print(f"Found {len(tables)} table(s): {', '.join(tables)}")
            print()

            # Inspect each table
            for table_name in tables:
                print("=" * 80)
                print(f"TABLE: {table_name}")
                print("=" * 80)

                # Get column information
                result = await conn.execute(
                    text(
                        """
                        SELECT
                            column_name,
                            data_type,
                            character_maximum_length,
                            is_nullable,
                            column_default
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                        AND table_name = :table_name
                        ORDER BY ordinal_position;
                    """
                    ),
                    {"table_name": table_name},
                )

                columns = result.fetchall()

                print("\nCOLUMNS:")
                print("-" * 80)
                print(f"{'Column Name':<30} {'Type':<25} {'Nullable':<10} {'Default'}")
                print("-" * 80)

                for col in columns:
                    col_name, data_type, max_length, nullable, default = col
                    type_str = data_type
                    if max_length:
                        type_str = f"{data_type}({max_length})"

                    default_str = str(default) if default else "None"
                    if len(default_str) > 30:
                        default_str = default_str[:27] + "..."

                    print(f"{col_name:<30} {type_str:<25} {nullable:<10} {default_str}")

                # Get row count
                result = await conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                row_count = result.scalar()
                print(f"\nTotal Rows: {row_count}")

                # Get primary keys
                result = await conn.execute(
                    text(
                        """
                        SELECT column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.table_schema = 'public'
                        AND tc.table_name = :table_name
                        AND tc.constraint_type = 'PRIMARY KEY'
                        ORDER BY kcu.ordinal_position;
                    """
                    ),
                    {"table_name": table_name},
                )
                pk_columns = [row[0] for row in result.fetchall()]
                if pk_columns:
                    print(f"Primary Key(s): {', '.join(pk_columns)}")

                # Get foreign keys
                result = await conn.execute(
                    text(
                        """
                        SELECT
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name
                        FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_schema = 'public'
                        AND tc.table_name = :table_name;
                    """
                    ),
                    {"table_name": table_name},
                )
                fk_columns = result.fetchall()
                if fk_columns:
                    print("\nForeign Keys:")
                    for fk in fk_columns:
                        print(f"  {fk[0]} -> {fk[1]}.{fk[2]}")

                # Show sample data if requested and table has data
                if show_sample_data and row_count > 0:
                    print(f"\nSAMPLE DATA (showing up to {limit} rows):")
                    print("-" * 80)

                    # Get sample rows
                    result = await conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT {limit}'))
                    rows = result.fetchall()
                    # Get column names from result keys (SQLAlchemy async API)
                    column_names = list(result.keys())

                    # Print column headers
                    header = " | ".join(f"{name[:15]:<15}" for name in column_names)
                    print(header)
                    print("-" * len(header))

                    # Print rows
                    for row in rows:
                        row_str = " | ".join(
                            f"{str(val)[:15]:<15}" if val is not None else f"{'NULL':<15}" for val in row
                        )
                        print(row_str)

                print()

            print("=" * 80)
            print("INSPECTION COMPLETE")
            print("=" * 80)

    except Exception as e:
        print(f"Error inspecting database: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main entry point."""
    import sys

    show_data = True
    limit = 5

    # Parse command line arguments
    if len(sys.argv) > 1:
        if "--no-data" in sys.argv:
            show_data = False
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            if idx + 1 < len(sys.argv):
                try:
                    limit = int(sys.argv[idx + 1])
                except ValueError:
                    print("Invalid limit value, using default: 5")

    await inspect_database(show_sample_data=show_data, limit=limit)


if __name__ == "__main__":
    asyncio.run(main())
