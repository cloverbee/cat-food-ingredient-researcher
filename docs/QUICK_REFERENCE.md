# 🚀 Quick Reference Guide

## Start Development Environment

### Start Everything
```bash
./start-dev.sh
```
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Start Individually

**Backend:**
```bash
source .venv/bin/activate
cd src
uvicorn api.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Common Commands

### Backend

```bash
# Seed database
python seed_data.py

# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Check API endpoints
curl http://localhost:8000/openapi.json | jq '.paths | keys'
```

### Frontend

```bash
# Install dependencies
npm install

# Generate types from backend
npm run generate-types

# Add shadcn component
npx shadcn@latest add [component-name]

# Build for production
npm run build
npm start
```

## API Endpoints Quick Reference

### Products
```bash
# List products
GET /api/v1/products

# Get product
GET /api/v1/products/{id}

# Create product
POST /api/v1/products
{
  "name": "Product Name",
  "brand": "Brand",
  "price": 29.99,
  "food_type": "Wet",
  "age_group": "Kitten"
}

# Update product
PUT /api/v1/products/{id}

# Delete product
DELETE /api/v1/products/{id}
```

### Search
```bash
# AI Search
POST /api/v1/search
{
  "query": "Find wet food for kittens"
}
```

### Ingredients
```bash
# List ingredients
GET /api/v1/ingredients

# Get ingredient
GET /api/v1/ingredients/{id}

# Create ingredient
POST /api/v1/ingredients
{
  "name": "Chicken",
  "description": "High-quality protein",
  "nutritional_value": {"protein": "20%"},
  "common_allergens": ["poultry"]
}
```

### Admin
```bash
# Bulk import
POST /api/v1/admin/ingest
{
  "file_content": "csv content",
  "filename": "products.csv"
}
```

## Testing APIs with curl

### Search Example
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Find wet food for kittens"}'
```

### Create Product Example
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "brand": "Test Brand",
    "price": 19.99,
    "food_type": "Wet",
    "age_group": "Kitten"
  }'
```

### Get All Products
```bash
curl http://localhost:8000/api/v1/products | jq
```

## Frontend Code Snippets

### Using API Hooks
```typescript
import { useProducts, useSearch } from '@/lib/api-hooks';

const { data: products, isLoading, error } = useProducts();
const { data: searchResult } = useSearch(query, true);
```

### Using API Client Directly
```typescript
import { apiClient } from '@/lib/api-client';

const result = await apiClient.search("your query");
const products = await apiClient.getProducts();
```

### Filter Products
```typescript
const [filters, setFilters] = useState<ProductFilters>({
  food_type: 'Wet',
  age_group: 'Kitten'
});
```

## Database

### PostgreSQL
```bash
# Connect to database
psql -h localhost -p 5433 -U postgres -d cat_food_research

# Common queries
SELECT * FROM cat_food_product;
SELECT * FROM ingredient;
SELECT COUNT(*) FROM cat_food_product WHERE food_type = 'Wet';
```

## Troubleshooting

### Backend won't start
```bash
# Check if port is in use
lsof -i :8000

# Verify virtual environment
source .venv/bin/activate
which python

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Clear cache and reinstall
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Type errors in frontend
```bash
cd frontend
npm run generate-types
```

### Database connection issues
- Check PostgreSQL is running
- Verify port 5433 is correct
- Check credentials in `src/core/config.py`

## Useful Links

- 📚 Backend API Docs: http://localhost:8000/docs
- 🎨 Frontend App: http://localhost:3000
- 📖 OpenAPI Schema: http://localhost:8000/openapi.json
- 🔧 React Query Devtools: Enabled in dev mode (bottom-left icon)

## Environment Variables

### Backend (in `.env` or `src/core/config.py`)
```bash
POSTGRES_SERVER=localhost
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=cat_food_research

GEMINI_API_KEY=your_api_key
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Frontend (in `.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Port Reference

- **3000** - Next.js frontend
- **8000** - FastAPI backend
- **5433** - PostgreSQL database
- **6333** - Qdrant vector database

## Git Workflow

```bash
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "description"

# Push
git push origin branch-name
```

## Helpful Aliases (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias catfood-backend="cd ~/workspace/cat-food-ingredient-researcher/src && source ../.venv/bin/activate && uvicorn api.main:app --reload --port 8000"
alias catfood-frontend="cd ~/workspace/cat-food-ingredient-researcher/frontend && npm run dev"
alias catfood-seed="cd ~/workspace/cat-food-ingredient-researcher && source .venv/bin/activate && python seed_data.py"
```

## Need Help?

- Check `PROJECT_OVERVIEW.md` for detailed documentation
- Check `FRONTEND_SETUP.md` for frontend-specific info
- Check `frontend/README.md` for component documentation
- Visit API docs at http://localhost:8000/docs
