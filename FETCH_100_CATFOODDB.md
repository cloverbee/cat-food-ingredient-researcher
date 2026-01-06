# Fetching 100 Popular Cat Foods from CatFoodDB

## Summary
Successfully fetched **96 popular cat food products** from CatFoodDB with shopping links from Amazon (51) and Chewy (35).

## Commands Used

### Fetch with Amazon Links (Rainforest API)
```bash
source .venv/bin/activate
python -m src.scripts.fetch_popular_cat_foods \
  --catfooddb-count 100 \
  --second-source rainforest_api \
  --petco-count 100 \
  --max-output 100 \
  --output cat_food_100_amazon.csv
```

### Alternative: Fetch with Petco Links
```bash
python -m src.scripts.fetch_popular_cat_foods \
  --catfooddb-count 100 \
  --second-source petco \
  --petco-count 100 \
  --max-output 100 \
  --output cat_food_100_petco.csv \
  --delay 2.0
```

### Fetch ONLY Amazon Links (Skip CatFoodDB)
If you want only Amazon links and no Chewy links:
```bash
python -m src.scripts.rainforest_api_fetcher \
  --type dry \
  --count 100 \
  --output cat_food_amazon_only.csv
```

## Import to Database

### Option 1: Append to Existing Database (Recommended)
Adds products without deleting existing ones:
```bash
source .venv/bin/activate
python -m src.scripts.import_products_csv_to_db --csv cat_food_100_amazon.csv
```

### Option 2: Replace All Products
Wipes existing products and imports fresh data:
```bash
python -m src.scripts.reset_and_import --yes --csv cat_food_100_amazon.csv
```

## Shopping URL Sources

The script supports these sources (instead of Chewy):
- **Rainforest API** (`--second-source rainforest_api`) - Gets Amazon links
- **Petco** (`--second-source petco`) - Gets Petco links
- **CSV** (`--second-source csv`) - Use existing CSV file

## Notes

- CatFoodDB pages typically have < 50 items each, so the script aggregates across multiple pages
- Shopping URLs from CatFoodDB often link to Chewy, but Rainforest API provides Amazon links
- The script automatically deduplicates products based on URL and name
- Products are prioritized by having both image_url and shopping_url
