# Cat Food Data Fetching Scripts

This directory contains scripts to fetch cat food product data from various sources.

## Available Scripts

### 1. `fetch_cat_food_data.py` - Web Scraper (General Purpose)

Fetches cat food products by scraping websites (Amazon, Chewy, Petco).

**⚠️ Important Legal Notice:**
- Web scraping may violate Terms of Service of some websites
- Always check robots.txt and respect rate limits
- Use responsibly and consider official APIs when available
- This script is for educational/research purposes

**Usage:**
```bash
# Fetch 100 dry food products from Amazon
python -m src.scripts.fetch_cat_food_data --source amazon --type dry --count 100

# Fetch 100 wet food products from Chewy
python -m src.scripts.fetch_cat_food_data --source chewy --type wet --count 100

# Fetch 100 dessert/treat products from all sources
python -m src.scripts.fetch_cat_food_data --source all --type dessert --count 100

# Custom output file and delay
python -m src.scripts.fetch_cat_food_data --source amazon --type dry --count 100 --output my_data.csv --delay 3.0
```

**Options:**
- `--source`: Data source (`amazon`, `chewy`, `petco`, or `all`)
- `--type`: Food type (`dry`, `wet`, or `dessert`)
- `--count`: Number of products to fetch (default: 100)
- `--output`: Output CSV filename (default: `cat_food_data.csv`)
- `--delay`: Delay between requests in seconds (default: 2.0)

### 2. `amazon_api_fetcher.py` - Amazon Product Advertising API (Recommended)

Uses the official Amazon Product Advertising API. **This is the recommended approach** as it's legal and more reliable.

**Setup:**
1. Sign up for Amazon Product Advertising API: https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html
2. Get your credentials:
   - Access Key
   - Secret Key <!-- pragma: allowlist secret -->
   - Associate Tag
3. Set environment variables:
   ```bash
   export AMAZON_ACCESS_KEY='your_access_key'
   export AMAZON_SECRET_KEY='your_secret_key'  # pragma: allowlist secret
   export AMAZON_ASSOCIATE_TAG='your_associate_tag'
   ```

   Or create a `.env` file:
   ```
   AMAZON_ACCESS_KEY=your_access_key
   AMAZON_SECRET_KEY=your_secret_key
   AMAZON_ASSOCIATE_TAG=your_associate_tag
   ```

4. Install the required package:
   ```bash
   pip install python-amazon-paapi
   ```

**Usage:**
```bash
# Fetch 100 dry food products
python -m src.scripts.amazon_api_fetcher --type dry --count 100

# Fetch 100 wet food products
python -m src.scripts.amazon_api_fetcher --type wet --count 100

# Fetch 100 dessert/treat products
python -m src.scripts.amazon_api_fetcher --type dessert --count 100 --output desserts.csv
```

### 3. `fetch_all_cat_food.py` - Fetch All Categories

Convenience script to fetch all three categories at once (100 dry, 100 wet, 100 dessert).

**Usage:**
```bash
python -m src.scripts.fetch_all_cat_food
```

This will generate:
- `cat_food_dry.csv` - 100 dry food products
- `cat_food_wet.csv` - 100 wet food products
- `cat_food_dessert.csv` - 100 dessert/treat products

### 4. `combine_csv_files.py` - Combine Multiple CSV Files

Combines multiple CSV files into one.

**Usage:**
```bash
python -m src.scripts.combine_csv_files cat_food_dry.csv cat_food_wet.csv cat_food_dessert.csv --output combined.csv
```

### 5. `generate_mock_cat_food_data.py` - Generate Mock Data (Testing/Fallback)

Generates realistic mock cat food data for testing or when real data fetching is unavailable.

**Usage:**
```bash
# Generate 100 mock dry food products
python -m src.scripts.generate_mock_cat_food_data --type dry --count 100

# Generate 100 mock wet food products
python -m src.scripts.generate_mock_cat_food_data --type wet --count 100

# Generate 100 mock dessert products
python -m src.scripts.generate_mock_cat_food_data --type dessert --count 100
```

### 6. `generate_all_mock_data.py` - Generate All Mock Categories

Convenience script to generate mock data for all three categories.

**Usage:**
```bash
python -m src.scripts.generate_all_mock_data
```

## Recommended Approach

### For Best Results:

1. **Use Amazon Product Advertising API** (`amazon_api_fetcher.py`)
   - ✅ Legal and official
   - ✅ More reliable
   - ✅ Better data quality
   - ⚠️ Requires API credentials

2. **Use Web Scraping** (`fetch_cat_food_data.py`) as fallback
   - ⚠️ May violate ToS
   - ⚠️ Less reliable (website structure changes)
   - ✅ No API credentials needed

### Quick Start - Fetch All Data:

```bash
# Option 1: Using Amazon API (recommended)
# First, set up credentials (see above)
python -m src.scripts.amazon_api_fetcher --type dry --count 100 --output cat_food_dry.csv
python -m src.scripts.amazon_api_fetcher --type wet --count 100 --output cat_food_wet.csv
python -m src.scripts.amazon_api_fetcher --type dessert --count 100 --output cat_food_dessert.csv

# Option 2: Using web scraping
python -m src.scripts.fetch_all_cat_food

# Combine all files
python -m src.scripts.combine_csv_files cat_food_dry.csv cat_food_wet.csv cat_food_dessert.csv --output cat_food_all.csv
```

## Data Format

All scripts output CSV files with the following columns:
- `name`: Product name
- `brand`: Brand name
- `price`: Price (float, optional)
- `age_group`: Age group (Kitten/Adult/Senior, optional)
- `food_type`: Food type (Dry/Wet/Dessert)
- `description`: Product description (optional)
- `full_ingredient_list`: Comma-separated ingredient list (optional)

## Importing Data

After generating CSV files, you can import them using the ingestion API:

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/ingest/csv" \
  -F "file=@cat_food_all.csv"

# Or use the FastAPI docs at http://localhost:8000/docs
```

## Troubleshooting

### Web Scraping Issues:
- **No products found**: Website structure may have changed. Try a different source.
- **Rate limiting**: Increase `--delay` parameter (e.g., `--delay 5.0`)
- **Connection errors**: Check your internet connection and try again

### Amazon API Issues:
- **Authentication errors**: Verify your credentials are set correctly
- **API limits**: Amazon API has rate limits. Wait and try again later
- **No results**: Try different search terms or check your Associate Tag

## Alternative Data Sources

If the scripts don't work, consider:
1. **Pet Food Databases**: Some specialized databases may have APIs
2. **Open Food Facts**: Has pet food data (https://world.openfoodfacts.org/)
3. **Manual Collection**: Use browser extensions or manual data entry
4. **Third-party APIs**: Services like ScraperAPI or SerpAPI (paid)

## Notes

- Web scraping is fragile and may break when websites update their structure
- Always respect robots.txt and rate limits
- Consider the legal implications of web scraping
- The Amazon API is the most reliable and legal option
