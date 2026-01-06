# Expand Database to 100 Products Guide

This guide explains how to expand your cat food product database from 38 items to 100 items using multiple sources.

## Quick Start

Run the expansion script:

```bash
python -m src.scripts.expand_to_100_products
```

This will:
1. Check your current database count
2. Fetch products from multiple sources (Amazon, Chewy, Petco)
3. Avoid duplicates
4. Import new products to reach 100 total

## Available Sources

The script supports fetching from:

1. **Web Scrapers** (default):
   - `amazon` - Amazon.com
   - `chewy` - Chewy.com
   - `petco` - Petco.com

2. **API Sources** (optional, requires API keys):
   - `rainforest` - Rainforest API (Amazon data)
   - `amazon-api` - Amazon Product Advertising API

## Usage Examples

### Basic Usage (Default: 100 products)
```bash
python -m src.scripts.expand_to_100_products
```

### Custom Target Count
```bash
python -m src.scripts.expand_to_100_products --target 150
```

### Dry Run (Preview without importing)
```bash
python -m src.scripts.expand_to_100_products --dry-run
```

### Specify Sources
```bash
# Only Amazon and Chewy
python -m src.scripts.expand_to_100_products --sources amazon chewy

# Include API sources (requires API keys)
python -m src.scripts.expand_to_100_products --sources amazon chewy petco rainforest
```

### Specify Food Types
```bash
# Only dry food
python -m src.scripts.expand_to_100_products --food-types dry

# Dry and wet food
python -m src.scripts.expand_to_100_products --food-types dry wet
```

### Adjust Request Delay
```bash
# Slower requests (more respectful)
python -m src.scripts.expand_to_100_products --delay 3.0

# Faster requests (may hit rate limits)
python -m src.scripts.expand_to_100_products --delay 1.0
```

## API Setup (Optional)

### Rainforest API
1. Sign up at https://www.rainforestapi.com/ (free tier: 100 requests/month)
2. Get your API key from the dashboard
3. Set environment variable:
   ```bash
   export RAINFOREST_API_KEY=your_api_key
   ```
   Or add to `.env` file:
   ```
   RAINFOREST_API_KEY=your_api_key
   ```

### Amazon Product Advertising API
1. Sign up at https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html
2. Get credentials (Access Key, Secret Key, Associate Tag)
3. Set environment variables:
   ```bash
   export AMAZON_ACCESS_KEY=your_access_key
   export AMAZON_SECRET_KEY=your_secret_key
   export AMAZON_ASSOCIATE_TAG=your_associate_tag
   ```
   Or add to `.env` file:
   ```
   AMAZON_ACCESS_KEY=your_access_key
   AMAZON_SECRET_KEY=your_secret_key
   AMAZON_ASSOCIATE_TAG=your_associate_tag
   ```

## How It Works

1. **Check Current Count**: Queries the database to see how many products you currently have
2. **Calculate Needed**: Determines how many more products are needed to reach the target
3. **Fetch from Sources**: Distributes fetching across selected sources and food types
4. **Deduplicate**: Checks against existing products by URL and name to avoid duplicates
5. **Import**: Uses the ingestion service to import new products into the database

## Product Sources Distribution

The script automatically distributes products across:
- **Sources**: Amazon, Chewy, Petco (and optionally Rainforest API, Amazon API)
- **Food Types**: Dry, Wet, Dessert/Treats
- **Shopping URLs**: Will come from the respective sources (Amazon, Chewy, Petco, etc.)
- **Images**: Will come from the respective sources (not just CatFoodDB)

## Output

- Products are saved to `expanded_products.csv` before import (for backup)
- Console output shows:
  - Current database count
  - Products fetched per source
  - Duplicates skipped
  - Final database count

## Troubleshooting

### No Products Fetched
- Check your internet connection
- Some websites may block scrapers - try different sources
- For API sources, verify your API keys are set correctly

### Rate Limiting
- Increase the `--delay` parameter (default: 2.0 seconds)
- Try fetching from fewer sources at once

### Duplicates
- The script automatically skips duplicates based on URL and name
- If you see many duplicates, try different food types or sources

### Database Connection Issues
- Ensure your database is running
- Check your `DATABASE_URL` environment variable
- Verify database credentials in your `.env` file

## Notes

- **Web Scraping**: Web scraping may violate Terms of Service of some websites. Use responsibly.
- **Rate Limiting**: The script includes delays between requests to be respectful to websites.
- **Images**: Images will come from the source websites (Amazon, Chewy, Petco, etc.), not just CatFoodDB.
- **Shopping URLs**: Shopping URLs will be from the respective sources, providing variety beyond just Chewy.
