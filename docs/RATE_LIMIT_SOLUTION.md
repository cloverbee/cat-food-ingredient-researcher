# Rate Limit Solution Guide

If you're getting 429 (Too Many Requests) or 503 (Service Unavailable) errors from web scrapers, here are solutions:

## Quick Solution: Use CSV Fallback

The easiest way to expand your database right now is to use existing CSV files:

```bash
python -m src.scripts.expand_to_100_products --use-csv-fallback
```

This will:
1. Try to fetch from scrapers (may fail due to rate limits)
2. **Automatically fall back** to existing CSV files (`cat_food_popular_merged.csv`, `cat_food_rainforest.csv`)
3. Import products from CSV files to reach 100 total

## Use Specific CSV Files

If you have specific CSV files you want to use:

```bash
python -m src.scripts.expand_to_100_products --csv-files cat_food_popular_merged.csv cat_food_rainforest.csv
```

## Better Solution: Use API Sources

API sources are more reliable and don't get rate limited as easily:

### Option 1: Rainforest API (Recommended - Free tier available)

1. Sign up at https://www.rainforestapi.com/ (free tier: 100 requests/month)
2. Get your API key
3. Set environment variable:
   ```bash
   export RAINFOREST_API_KEY=your_api_key
   ```
4. Run:
   ```bash
   python -m src.scripts.expand_to_100_products --sources rainforest
   ```

### Option 2: Amazon Product Advertising API

1. Sign up at https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html
2. Get credentials (Access Key, Secret Key, Associate Tag)
3. Set environment variables:
   ```bash
   export AMAZON_ACCESS_KEY=your_access_key
   export AMAZON_SECRET_KEY=your_secret_key
   export AMAZON_ASSOCIATE_TAG=your_associate_tag
   ```
4. Run:
   ```bash
   python -m src.scripts.expand_to_100_products --sources amazon-api
   ```

### Option 3: Combine API Sources

```bash
python -m src.scripts.expand_to_100_products --sources rainforest amazon-api
```

## Improved Error Handling

The script now includes:
- ✅ **Retry logic** with exponential backoff (3 attempts)
- ✅ **Better error messages** explaining what went wrong
- ✅ **CSV fallback** option
- ✅ **Prioritizes API sources** (more reliable)

## Increase Delay for Scrapers

If you want to keep using scrapers, increase the delay:

```bash
python -m src.scripts.expand_to_100_products --delay 5.0
```

This waits 5 seconds between requests (default is 3 seconds).

## Recommended Approach

For best results, use this combination:

```bash
# Try API sources first, fall back to CSV if needed
python -m src.scripts.expand_to_100_products --sources rainforest --use-csv-fallback
```

Or if you don't have API keys yet:

```bash
# Use CSV files directly
python -m src.scripts.expand_to_100_products --use-csv-fallback
```

## Troubleshooting

### Still getting rate limited?
- Use `--use-csv-fallback` to use existing CSV files
- Set up Rainforest API (free tier available)
- Wait a few hours and try again with increased delay

### No products imported?
- Check that CSV files exist in the project root
- Verify CSV files have the correct format (name, brand, price, etc.)
- Check database connection

### Want to see what would be imported?
Use dry-run mode:
```bash
python -m src.scripts.expand_to_100_products --use-csv-fallback --dry-run
```
