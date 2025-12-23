# Product Images and Shopping Links Feature

## Overview

This feature adds product images and direct shopping links (Amazon affiliate links) to cat food products, allowing users to see product images and purchase products immediately.

## What's New

### Database Changes
- Added `image_url` column to `cat_food_product` table
- Added `shopping_url` column to `cat_food_product` table

### API Changes
- Product schemas now include `image_url` and `shopping_url` fields
- CSV ingestion supports the new fields
- Amazon API fetcher automatically extracts images and generates affiliate links

### Frontend Changes
- Product cards display product images
- "Buy on Amazon" button on product cards and detail pages
- Images are displayed with proper fallback handling

## Database Migration

Run the migration to add the new columns:

```bash
alembic upgrade head
```

Or if using the migration file directly:
```bash
# The migration file is at: migrations/versions/add_image_url_and_shopping_url.py
```

## Using the Amazon API Fetcher

The Amazon API fetcher now automatically:
1. **Extracts product images** from Amazon's API
2. **Generates affiliate links** using your Associate Tag

### Example Usage

```bash
# Fetch products with images and shopping links
python -m src.scripts.amazon_api_fetcher --type dry --count 100
```

The generated CSV will include:
- `image_url`: Direct link to product image
- `shopping_url`: Amazon affiliate link (e.g., `https://www.amazon.com/dp/ASIN?tag=your-associate-tag`)

### CSV Format

Your CSV files should now include these columns:

```csv
name,brand,price,age_group,food_type,description,full_ingredient_list,image_url,shopping_url
Product Name,Brand Name,29.99,Adult,Dry,Description here,"Ingredient1, Ingredient2",https://example.com/image.jpg,https://amazon.com/dp/ASIN?tag=yoursite-20
```

## Frontend Display

### Product Cards
- Product images are displayed at the top of each card
- "Buy on Amazon" button appears at the bottom if `shopping_url` is available
- Images have hover effects and proper loading states

### Product Detail Page
- Large product image displayed at the top
- Prominent "Buy on Amazon" button
- All product information remains accessible

## Amazon Affiliate Links

The shopping links are automatically generated as Amazon affiliate links in the format:
```
https://www.amazon.com/dp/{ASIN}?tag={ASSOCIATE_TAG}
```

**Important**:
- You must have an Amazon Associates account
- Your Associate Tag must be set in the `.env` file as `AMAZON_ASSOCIATE_TAG`
- Affiliate links allow you to earn commissions on purchases

## Image Handling

### Image Sources
- Images are fetched from Amazon's Product Advertising API
- Images use Next.js Image component for optimization
- Fallback handling if images fail to load

### Image Requirements
- Images should be publicly accessible URLs
- Recommended format: JPG or PNG
- Recommended size: At least 400x400 pixels for best display

## Example Workflow

1. **Fetch products with images and links:**
   ```bash
   python -m src.scripts.fetch_all_amazon
   ```

2. **Import to database:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/ingest/csv" \
     -F "file=@cat_food_all_amazon.csv"
   ```

3. **View in frontend:**
   - Products will display with images
   - Click "Buy on Amazon" to purchase

## Troubleshooting

### Images Not Displaying
- Check that `image_url` is set in the database
- Verify the image URL is accessible
- Check browser console for CORS or loading errors

### Shopping Links Not Working
- Verify `AMAZON_ASSOCIATE_TAG` is set correctly
- Check that your Associate Tag is active
- Ensure the ASIN is valid

### Migration Issues
- Make sure you're running the latest migration
- Check database connection
- Verify table structure matches the model

## API Endpoints

All existing endpoints now return `image_url` and `shopping_url`:

- `GET /api/v1/products` - List all products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/ingest/csv` - Import products with images/links

## Security Notes

- Affiliate links are safe to display publicly
- Images should be from trusted sources (Amazon API)
- Always use `rel="noopener noreferrer"` for external links (already implemented)

## Future Enhancements

Potential improvements:
- Image caching and CDN integration
- Multiple image support (gallery)
- Price tracking and alerts
- Comparison shopping links (multiple retailers)
