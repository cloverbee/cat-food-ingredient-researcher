from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.controllers import ingestion_controller, ingredient_controller, product_controller, search_controller
from src.core.config import settings
from src.infrastructure.ai.llama_index_config import configure_llama_index

# Conditional docs configuration - disable in production
docs_config = {}
if settings.is_production:
    docs_config = {"docs_url": None, "redoc_url": None, "openapi_url": None}
else:
    docs_config = {"openapi_url": f"{settings.API_V1_STR}/openapi.json"}

app = FastAPI(title=settings.PROJECT_NAME, **docs_config)

# Configure CORS
# Get allowed origins from environment or use defaults
import os

allowed_origins = [
    "http://localhost:3000",  # Next.js frontend (default)
    "http://localhost:3001",  # Next.js frontend (alternate port)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Add production frontend URL from environment if provided
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# For production: add Vercel deployment URLs
# Pattern for Vercel: https://your-app.vercel.app and https://your-app-*.vercel.app (preview deployments)
vercel_domain = os.getenv("VERCEL_DOMAIN")
if vercel_domain:
    allowed_origins.append(f"https://{vercel_domain}")
    # Vercel preview deployments follow pattern: your-app-git-branch-username.vercel.app
    # We'll use allow_origin_regex for wildcard support

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
async def startup_event():
    configure_llama_index()


app.include_router(ingredient_controller.router, prefix=f"{settings.API_V1_STR}/ingredients", tags=["ingredients"])
app.include_router(product_controller.router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(ingestion_controller.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(search_controller.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])


@app.get("/")
async def root():
    return {"message": "Welcome to Cat Food Ingredient Researcher API"}
