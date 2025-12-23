# Rainforest API Setup Guide (Easy Alternative to Amazon PA-API)

Rainforest API provides Amazon product data without requiring an Amazon Associates account or sales history.

## Why Rainforest API?

✅ **No sales requirements** - Just sign up and get an API key
✅ **Free tier** - 100 requests/month (enough for 100 products)
✅ **Real Amazon data** - Product images, prices, shopping links
✅ **Simple REST API** - Easy to use with Python requests

## Step 1: Sign Up for Rainforest API

1. Go to [Rainforest API](https://www.rainforestapi.com/)
2. Click **"Try for free"** or **"Sign Up"**
3. Create an account with your email
4. Verify your email address

## Step 2: Get Your API Key

1. Log into your Rainforest API dashboard
2. Find your **API Key** on the dashboard (it looks like a long string of letters and numbers)
3. Copy this key - you'll need it!

## Step 3: Configure Your API Key

### Option A: Environment Variable (Recommended)

```bash
export RAINFOREST_API_KEY='your_api_key_here'  # pragma: allowlist secret
```

### Option B: .env File

Add to your `.env` file in the project root:

```env
RAINFOREST_API_KEY=your_api_key_here
```

## Step 4: Run the Fetcher

```bash
# Fetch 100 cat food products (uses ~10 API requests)
python -m src.scripts.rainforest_api_fetcher --count 100

# Fetch specific food types
python -m src.scripts.rainforest_api_fetcher --type dry --count 30
python -m src.scripts.rainforest_api_fetcher --type wet --count 30
python -m src.scripts.rainforest_api_fetcher --type dessert --count 30
```

## API Usage & Limits

| Plan | Requests/Month | Cost |
|------|----------------|------|
| Free Tier | 100 | $0 |
| Starter | 2,500 | $49/mo |
| Pro | 10,000 | $149/mo |

**Note**: Each search request returns up to 10 products, so fetching 100 products uses ~10 requests.

## Troubleshooting

### Error: "Missing Rainforest API key"
Make sure you've set the `RAINFOREST_API_KEY` environment variable or added it to your `.env` file.

### Error: "API request failed"
- Check your API key is correct
- Verify you haven't exceeded your monthly limit
- Check the Rainforest API status page

### No products found
- Try different search terms
- Make sure you're searching in the correct Amazon domain

## Output Format

The fetcher creates a CSV file with:
- `name` - Product name
- `brand` - Brand name
- `price` - Price in USD
- `age_group` - Kitten/Adult/Senior (if detected)
- `food_type` - Dry/Wet/Dessert
- `description` - Product description
- `full_ingredient_list` - Ingredients (if available)
- `image_url` - Product image URL
- `shopping_url` - Amazon shopping link

## Resources

- [Rainforest API Documentation](https://docs.trajectdata.com/)
- [Rainforest API Dashboard](https://app.rainforestapi.com/)
