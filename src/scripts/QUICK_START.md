# Quick Start Guide - Fetching Cat Food Data

## 🚀 Fastest Way to Get Started

### Option 1: Generate Mock Data (Immediate - No Setup Required)

If you need data quickly for testing or development:

```bash
# Generate all categories (100 dry + 100 wet + 100 dessert)
python -m src.scripts.generate_all_mock_data

# This creates:
# - cat_food_dry_mock.csv
# - cat_food_wet_mock.csv
# - cat_food_dessert_mock.csv
```

Then combine them:
```bash
python -m src.scripts.combine_csv_files cat_food_dry_mock.csv cat_food_wet_mock.csv cat_food_dessert_mock.csv --output cat_food_all.csv
```

### Option 2: Use Amazon Product Advertising API (Recommended for Production)

**Setup (one-time):**
1. Sign up: https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html
2. Get credentials (Access Key, Secret Key, Associate Tag)
3. Install SDK: `pip install python-amazon-paapi`
4. Set environment variables:
   ```bash
   export AMAZON_ACCESS_KEY='your_key'
   export AMAZON_SECRET_KEY='your_secret'  # pragma: allowlist secret
   export AMAZON_ASSOCIATE_TAG='your_tag'
   ```

**Fetch data:**
```bash
# Option A: Fetch all categories at once (easiest)
python -m src.scripts.fetch_all_amazon

# Option B: Fetch categories individually
python -m src.scripts.amazon_api_fetcher --type dry --count 100 --output cat_food_dry.csv
python -m src.scripts.amazon_api_fetcher --type wet --count 100 --output cat_food_wet.csv
python -m src.scripts.amazon_api_fetcher --type dessert --count 100 --output cat_food_dessert.csv

# Combine (if using Option B)
python -m src.scripts.combine_csv_files cat_food_dry.csv cat_food_wet.csv cat_food_dessert.csv --output cat_food_all.csv
```

### Option 3: Web Scraping (Fallback - May Have Issues)

```bash
# Fetch from Amazon (may be blocked)
python -m src.scripts.fetch_cat_food_data --source amazon --type dry --count 100

# Or fetch all at once
python -m src.scripts.fetch_all_cat_food
```

## 📊 Import Data to Database

After generating CSV files, import them:

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/ingest/csv" \
  -F "file=@cat_food_all.csv"

# Or visit http://localhost:8000/docs and use the /ingest/csv endpoint
```

## 🎯 Recommended Workflow

1. **Start with mock data** for development/testing
2. **Set up Amazon API** for production data
3. **Use web scraping** only as last resort

## ⚠️ Important Notes

- **Mock data**: Perfect for testing, not real products
- **Amazon API**: Best quality, requires setup, legal
- **Web scraping**: May violate ToS, less reliable, no setup needed
