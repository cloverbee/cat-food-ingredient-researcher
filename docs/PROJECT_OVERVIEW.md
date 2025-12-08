# 🐱 Cat Food Ingredient Researcher

A full-stack application for researching and analyzing cat food products and their ingredients using AI-powered search.

## 📋 Project Structure

```
cat-food-ingredient-researcher/
├── frontend/              # Next.js frontend application
├── src/                   # FastAPI backend application
│   ├── api/              # API controllers and routes
│   ├── core/             # Core configuration
│   ├── domain/           # Business logic, models, schemas
│   └── infrastructure/   # External services (AI, vector DB)
├── migrations/           # Alembic database migrations
├── seed_data.py          # Database seeding script
└── requirements.txt      # Python dependencies
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Activate Python virtual environment
source .venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the backend server
cd src
uvicorn api.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM with async support
- **Google Gemini** - AI model for natural language search
- **LlamaIndex** - LLM orchestration framework
- **Qdrant** - Vector database (for future semantic search)

### Frontend
- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS 4** - Modern styling
- **shadcn/ui** - UI component library
- **TanStack Query** - Data fetching and caching
- **openapi-typescript** - Type generation from OpenAPI schema

## 📊 Database Schema

### Tables

**cat_food_product**
- `id` - Primary key
- `name` - Product name
- `brand` - Brand name
- `price` - Price in dollars
- `age_group` - Target age (Kitten, Adult, Senior)
- `food_type` - Type (Wet, Dry, Snack)
- `description` - Product description
- `full_ingredient_list` - Comma-separated ingredients
- `embedding_id` - Vector DB reference (future use)

**ingredient**
- `id` - Primary key
- `name` - Ingredient name (unique)
- `description` - Description
- `nutritional_value` - JSONB with nutrition data
- `common_allergens` - JSONB array of allergens

**product_ingredient_association**
- Many-to-many relationship table

## 🎯 Key Features

### 🔍 AI-Powered Search
Natural language search using Google Gemini:
```
Query: "Find wet food for kittens"
Returns: List of wet food products for kittens with details
```

### 📊 Product Management
- Create, read, update, delete products
- Filter by food type, age group, brand, price
- View detailed product information
- See all ingredients in each product

### 🧪 Ingredient Management
- Manage ingredient database
- View nutritional information
- Track allergens
- See which products use each ingredient

### 📥 Bulk Import
- Import products from CSV files
- Automatic ingredient extraction
- Validation and error handling

## 🔌 API Endpoints

### Products
- `GET /api/v1/products` - List all products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products` - Create product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Ingredients
- `GET /api/v1/ingredients` - List all ingredients
- `GET /api/v1/ingredients/{id}` - Get ingredient details
- `POST /api/v1/ingredients` - Create ingredient
- `PUT /api/v1/ingredients/{id}` - Update ingredient
- `DELETE /api/v1/ingredients/{id}` - Delete ingredient

### Search
- `POST /api/v1/search` - AI-powered natural language search

### Admin
- `POST /api/v1/admin/ingest` - Bulk import products from CSV

## 🔧 Configuration

### Backend Configuration (`src/core/config.py`)
```python
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=cat_food_research
POSTGRES_PORT=5433

GEMINI_API_KEY=your_gemini_api_key
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Frontend Configuration (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 Seed Data

The project includes a comprehensive seed data script with:
- 25 realistic ingredients
- 20 cat food products
- Multiple brands, age groups, and food types

To seed the database:
```bash
python seed_data.py
```

## 🔄 Type Generation

The frontend can automatically generate TypeScript types from the backend OpenAPI schema:

```bash
cd frontend
npm run generate-types
```

This requires the backend to be running and will:
1. Fetch the OpenAPI schema from `http://localhost:8000/openapi.json`
2. Generate TypeScript types
3. Use `jq` to display available endpoints

## 🚦 Development Workflow

### Making API Changes
1. Update FastAPI models/schemas in `src/domain/`
2. Update controllers in `src/api/controllers/`
3. Test API at `http://localhost:8000/docs`
4. Regenerate frontend types: `npm run generate-types`
5. Update frontend components as needed

### Adding New Features
1. **Backend**: Add models → schemas → services → controllers
2. **Frontend**: Update types → API client → hooks → components

## 🧪 Testing

### Backend API Testing
Visit `http://localhost:8000/docs` for interactive API documentation and testing.

### Frontend Testing
1. Ensure backend is running
2. Open `http://localhost:3000`
3. Test features:
   - Search functionality
   - Product filtering
   - Product details
   - CRUD operations

## 📚 Documentation

- **Backend API**: http://localhost:8000/docs
- **Frontend README**: `frontend/README.md`
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🐛 Troubleshooting

### "Connection refused" errors
- Verify PostgreSQL is running on port 5433
- Check backend is running on port 8000
- Ensure frontend is configured to use correct API URL

### Import errors in backend
- Activate virtual environment: `source .venv/bin/activate`
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Type errors in frontend
- Regenerate types: `npm run generate-types`
- Check TypeScript version compatibility
- Verify backend is running

### Search not working
- Check Gemini API key is configured
- Verify `llama_index_config.py` is using correct model
- Check API logs for errors

## 🚀 Deployment

### Backend
- Use Docker or deploy to platforms like Heroku, Railway, or Render
- Configure production database
- Set environment variables for API keys

### Frontend
- Deploy to Vercel (recommended for Next.js)
- Set `NEXT_PUBLIC_API_URL` to production backend URL
- Build: `npm run build`

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📝 License

Private project

## 👥 Contact

For questions or issues, please contact the development team.

