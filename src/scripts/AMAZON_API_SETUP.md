# Amazon Product Advertising API Setup Guide

This guide will help you set up the Amazon Product Advertising API to fetch cat food product data.

## Step 1: Sign Up for Amazon Associates

1. Go to [Amazon Associates](https://affiliate-program.amazon.com/)
2. Sign up for an account (if you don't have one)
3. Complete the application process
4. Once approved, you'll get an **Associate Tag** (e.g., `yourstore-20`)

## Step 2: Sign Up for Product Advertising API

1. Go to [Amazon Product Advertising API](https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html)
2. Click "Sign Up" or "Get Started"
3. Log in with your Amazon Associates account
4. Complete the API registration

## Step 3: Get Your API Credentials

After registration, you'll receive:

1. **Access Key** (also called Access Key ID)
2. **Secret Key** (also called Secret Access Key)
3. **Associate Tag** (from your Associates account)

⚠️ **Important**: Keep these credentials secure and never commit them to version control!

## Step 4: Install Required Package

Install the community-maintained Amazon PA-API wrapper:

```bash
pip install python-amazon-paapi
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Step 5: Configure Credentials

You have two options:

### Option A: Environment Variables (Recommended for Production)

```bash
export AMAZON_ACCESS_KEY='your_access_key_here'
export AMAZON_SECRET_KEY='your_secret_key_here'  # pragma: allowlist secret
export AMAZON_ASSOCIATE_TAG='your_associate_tag_here'
export AMAZON_COUNTRY='US'  # Optional, defaults to US
```

### Option B: .env File (Recommended for Development)

Create a `.env` file in the project root (same directory as `requirements.txt`):

```env
AMAZON_ACCESS_KEY=your_access_key_here
AMAZON_SECRET_KEY=your_secret_key_here
AMAZON_ASSOCIATE_TAG=your_associate_tag_here
AMAZON_COUNTRY=US
```

⚠️ **Important**: Add `.env` to your `.gitignore` file to avoid committing credentials!

### Supported Countries

The `AMAZON_COUNTRY` variable supports:
- `US` - United States (default)
- `UK` - United Kingdom
- `DE` - Germany
- `FR` - France
- `JP` - Japan
- `CA` - Canada
- And many more...

## Step 6: Test the Setup

Run a test fetch:

```bash
# Fetch 10 dry food products (small test)
python -m src.scripts.amazon_api_fetcher --type dry --count 10
```

If successful, you should see:
```
✅ Successfully fetched 10 products
📁 Saved to: cat_food_dry_amazon.csv
```

## Step 7: Fetch All Categories

Once everything works, fetch all three categories:

```bash
# Fetch 100 dry food products
python -m src.scripts.amazon_api_fetcher --type dry --count 100 --output cat_food_dry.csv

# Fetch 100 wet food products
python -m src.scripts.amazon_api_fetcher --type wet --count 100 --output cat_food_wet.csv

# Fetch 100 dessert/treat products
python -m src.scripts.amazon_api_fetcher --type dessert --count 100 --output cat_food_dessert.csv
```

Or use the convenience script to fetch all at once:

```bash
python -m src.scripts.fetch_all_amazon
```

Then combine them:

```bash
python -m src.scripts.combine_csv_files cat_food_dry.csv cat_food_wet.csv cat_food_dessert.csv --output cat_food_all.csv
```

## Troubleshooting

### Error: "Missing Amazon API credentials"

**Solution**: Make sure you've set all three environment variables:
- `AMAZON_ACCESS_KEY`
- `AMAZON_SECRET_KEY`
- `AMAZON_ASSOCIATE_TAG`

Check that your `.env` file is in the project root and has the correct format.

### Error: "python-amazon-paapi is not installed"

**Solution**: Install the package:
```bash
pip install python-amazon-paapi
```

### Error: "InvalidSignatureException" or "InvalidAccessKeyIdException"

**Solution**:
- Double-check your Access Key and Secret Key
- Make sure there are no extra spaces or quotes
- Verify your credentials in the Amazon API console

### Error: "InvalidPartnerTagException"

**Solution**:
- Verify your Associate Tag is correct
- Make sure your Associates account is approved
- Check that the tag format is correct (e.g., `yourstore-20`)

### Error: Rate Limiting (429 errors)

**Solution**:
- Amazon API has rate limits
- The script automatically handles this with delays
- If you see frequent rate limit errors, reduce the `--count` or wait between runs

### No Products Found

**Solution**:
- Try different search terms
- Check that the search index "PetSupplies" is available in your region
- Verify your API account has access to product data

## API Limits

- **Items per request**: Maximum 10 items per API call
- **Rate limits**: Varies by account type (check your API dashboard)
- **Search index**: Must use "PetSupplies" for pet food products

## Cost

The Amazon Product Advertising API is **free** to use, but:
- You must be an approved Amazon Associate
- You must comply with Amazon's API terms of service
- There are rate limits based on your account type

## Security Best Practices

1. ✅ Never commit credentials to git
2. ✅ Use `.env` file for local development (and add to `.gitignore`)
3. ✅ Use environment variables for production
4. ✅ Rotate credentials if compromised
5. ✅ Don't share credentials in chat/email

## Additional Resources

- [Amazon Product Advertising API Documentation](https://webservices.amazon.com/paapi5/documentation/)
- [Amazon Associates Central](https://affiliate-program.amazon.com/)
- [API Status Dashboard](https://status.aws.amazon.com/)
- [python-amazon-paapi Documentation](https://github.com/sergioteula/python-amazon-paapi)

## Need Help?

If you encounter issues:
1. Check the error message carefully
2. Verify all credentials are correct
3. Check Amazon API status
4. Review the troubleshooting section above
