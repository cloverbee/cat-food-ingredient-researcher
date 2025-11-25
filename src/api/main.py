from fastapi import FastAPI
from src.core.config import settings
from src.infrastructure.ai.llama_index_config import configure_llama_index

from src.api.controllers import ingredient_controller, product_controller, ingestion_controller, search_controller

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

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
