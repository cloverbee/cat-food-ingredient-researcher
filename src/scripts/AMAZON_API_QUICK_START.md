# Amazon API Quick Start

## 🚀 Get Started in 5 Minutes

### Step 1: Install the SDK

```bash
pip install python-amazon-paapi
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Get Amazon API Credentials

1. Sign up: https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html
2. Get your credentials:
   - Access Key
   - Secret Key
   - Associate Tag

### Step 3: Set Credentials

Create a `.env` file in the project root:

```env
AMAZON_ACCESS_KEY=your_access_key_here
AMAZON_SECRET_KEY=your_secret_key_here
AMAZON_ASSOCIATE_TAG=your_associate_tag_here
```

### Step 4: Fetch Data

**Fetch all categories at once:**
```bash
python -m src.scripts.fetch_all_amazon
```

**Or fetch individually:**
```bash
# Dry food
python -m src.scripts.amazon_api_fetcher --type dry --count 100

# Wet food
python -m src.scripts.amazon_api_fetcher --type wet --count 100

# Dessert/Treats
python -m src.scripts.amazon_api_fetcher --type dessert --count 100
```

### Step 5: Combine Files (if needed)

```bash
python -m src.scripts.combine_csv_files \
  cat_food_dry_amazon.csv \
  cat_food_wet_amazon.csv \
  cat_food_dessert_amazon.csv \
  --output cat_food_all_amazon.csv
```

### Step 6: Import to Database

```bash
curl -X POST "http://localhost:8000/api/v1/ingest/csv" \
  -F "file=@cat_food_all_amazon.csv"
```

## 📚 Full Documentation

See `AMAZON_API_SETUP.md` for detailed setup instructions and troubleshooting.

## ⚡ Quick Commands Reference

```bash
# Test with small count
python -m src.scripts.amazon_api_fetcher --type dry --count 10

# Fetch all categories
python -m src.scripts.fetch_all_amazon

# Combine CSV files
python -m src.scripts.combine_csv_files file1.csv file2.csv file3.csv --output combined.csv
```
