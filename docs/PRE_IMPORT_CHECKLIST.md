# Pre-Import Checklist

This guide outlines the essential steps you should take **before importing new data** into your database to ensure data integrity and prevent data loss.

## 📋 Quick Checklist

- [ ] **1. Backup current database**
- [ ] **2. Inspect current database state**
- [ ] **3. Validate new data format**
- [ ] **4. Check for duplicates**
- [ ] **5. Run dry-run/preview**
- [ ] **6. Verify database constraints**
- [ ] **7. Check disk space**
- [ ] **8. Review import script**

---

## 1. Backup Current Database ✅

**Always backup before importing!** This allows you to restore if something goes wrong.

### Using the Backup Script

```bash
# Create a timestamped backup
python -m src.scripts.backup_database

# Or specify a custom output directory
python -m src.scripts.backup_database --output-dir backups/before_import_2024-01-15
```

This will create CSV backups of:
- `cat_food_product` table
- `ingredient` table
- `product_ingredient_association` table
- `user` table (if exists)

Backups are saved to `backups/YYYYMMDD_HHMMSS/` by default.

### Manual PostgreSQL Backup (Alternative)

If you prefer a full PostgreSQL dump:

```bash
# Using pg_dump (replace with your connection details)
pg_dump -h localhost -U postgres -d cat_food_research > backup_$(date +%Y%m%d_%H%M%S).sql

# Or using docker if your DB is in a container
docker exec cat_food_db pg_dump -U postgres cat_food_research > backup.sql
```

---

## 2. Inspect Current Database State 🔍

Check what's currently in your database before importing:

```bash
# View database structure and current data
python scripts/inspect_database.py

# View without sample data (faster)
python scripts/inspect_database.py --no-data

# View with more sample rows
python scripts/inspect_database.py --limit 10
```

This shows you:
- Current row counts for each table
- Table structure and constraints
- Sample data to verify current state

**Note the current product count** - this helps you verify the import worked correctly.

---

## 3. Validate New Data Format 📄

Before importing, verify your data file matches the expected format.

### For CSV Files

Check required columns:
- `name` (required)
- `brand` (required)
- `price` (optional)
- `age_group` (optional: kitten, adult, senior)
- `food_type` (optional: wet, dry)
- `description` (optional)
- `ingredients` (optional, comma-separated)

### For Excel Files

Verify columns match what the script expects:
- Name column (for matching)
- Description column (optional)
- Ingredient column (for updates)

### Quick Validation

```bash
# Preview CSV file
head -n 5 your_data.csv

# Check Excel file structure
python -c "import pandas as pd; df = pd.read_excel('your_file.xlsx'); print(df.columns.tolist()); print(df.head())"
```

---

## 4. Check for Duplicates 🔄

Identify potential duplicates before importing:

### Check Existing Products

```bash
# Query database for existing products
python scripts/query_database.py
```

### For CSV Imports

The ingestion service automatically checks for duplicates by:
- Product name + brand combination
- Shopping URL (if provided)

But you can manually check:

```python
# Quick duplicate check script
import pandas as pd
from src.core.database import AsyncSessionLocal
from sqlalchemy import select
from src.domain.models.product import CatFoodProduct

# Read your CSV
df = pd.read_csv("your_data.csv")

# Check against database (example)
async def check_duplicates():
    async with AsyncSessionLocal() as db:
        for _, row in df.iterrows():
            result = await db.execute(
                select(CatFoodProduct).where(
                    CatFoodProduct.name.ilike(f"%{row['name']}%"),
                    CatFoodProduct.brand.ilike(f"%{row['brand']}%")
                )
            )
            if result.scalars().first():
                print(f"Potential duplicate: {row['name']} - {row['brand']}")
```

---

## 5. Run Dry-Run/Preview 🧪

Many import scripts support dry-run mode to preview changes without committing:

### CSV Import

The ingestion service will show you what would be imported, but you can also:

```bash
# Check the CSV format first
python -m src.scripts.import_products_csv_to_db --csv your_data.csv
# Review the output before confirming
```

### Excel Update

```bash
# The update script will show you what will be updated
python -m src.scripts.update_products_from_excel --excel "cat food data.xlsx"
# Review the output - it shows which products will be updated
```

### Rollback Script (Preview)

```bash
# See what would be deleted (if rolling back)
python -m src.scripts.rollback_to_38_products --dry-run
```

---

## 6. Verify Database Constraints 🔒

Ensure your database schema is up-to-date:

```bash
# Check if migrations are applied
alembic current

# Apply any pending migrations
alembic upgrade head
```

Key constraints to verify:
- **Primary keys**: `id` columns exist
- **Foreign keys**: `product_ingredient_association` references are valid
- **Unique constraints**: `ingredient.name` must be unique
- **Required fields**: `product.name` and `product.brand` cannot be NULL

---

## 7. Check Disk Space 💾

Ensure you have enough disk space for:
- Database growth
- Backup files
- Log files

```bash
# Check disk space
df -h

# Check database size (PostgreSQL)
docker exec cat_food_db psql -U postgres -d cat_food_research -c "SELECT pg_size_pretty(pg_database_size('cat_food_research'));"
```

---

## 8. Review Import Script 📝

Before running, review the import script to understand:
- What data it will import
- How it handles duplicates
- What happens on errors
- Whether it uses transactions (can rollback)

### Key Import Scripts

1. **CSV Import**: `src/scripts/import_products_csv_to_db.py`
   - Uses `IngestionService` (same as API endpoint)
   - Handles duplicates automatically
   - Creates products and ingredients

2. **Excel Update**: `src/scripts/update_products_from_excel.py`
   - Updates existing products by name
   - Updates description and ingredients
   - Shows which products were found/not found

3. **Rollback**: `src/scripts/rollback_to_38_products.py`
   - Deletes products with ID > 38
   - Use `--dry-run` first!

---

## 🚀 Ready to Import?

Once you've completed the checklist:

1. **Double-check your backup** - Verify backup files exist
2. **Run the import** - Execute your import script
3. **Verify results** - Check row counts and sample data
4. **Test the application** - Make sure everything works

### After Import

```bash
# Verify import worked
python scripts/inspect_database.py

# Check product count increased
python -c "from src.core.database import AsyncSessionLocal; from sqlalchemy import select, func; from src.domain.models.product import CatFoodProduct; import asyncio; asyncio.run((lambda: (lambda db: db.execute(select(func.count(CatFoodProduct.id))).scalar())(AsyncSessionLocal()))())"
```

---

## ⚠️ Common Mistakes to Avoid

1. **Skipping backup** - Always backup first!
2. **Not checking data format** - Verify CSV/Excel columns match expected format
3. **Importing duplicates** - Check for existing products first
4. **Not testing on small dataset** - Try with 1-2 rows first
5. **Running in production without dry-run** - Always test first

---

## 🔄 Rollback Plan

If something goes wrong:

1. **Stop the import** - If it's still running, cancel it
2. **Check what was imported** - Use `inspect_database.py`
3. **Restore from backup** - Use your backup CSV files or SQL dump
4. **Or use rollback script** - If you need to delete specific products

### Restore from CSV Backup

```python
# Example restore script (create if needed)
import pandas as pd
from src.core.database import AsyncSessionLocal
from src.domain.models.product import CatFoodProduct

async def restore_from_backup(backup_path):
    df = pd.read_csv(backup_path)
    async with AsyncSessionLocal() as db:
        # Clear current data (be careful!)
        # Then import from backup
        pass
```

---

## 📚 Related Documentation

- [Database Connection Guide](DATABASE_CONNECTION_GUIDE.md)
- [Expand Database Guide](EXPAND_DATABASE_GUIDE.md)
- [Project Overview](PROJECT_OVERVIEW.md)

---

**Remember**: When in doubt, backup first, test with small data, then proceed with full import!
