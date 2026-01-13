from typing import Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings using Pydantic Settings.
    All sensitive values MUST be provided via environment variables.
    """

    # Application
    PROJECT_NAME: str = "Cat Food Ingredient Researcher"
    API_V1_STR: str = "/api/v1"
    # Railway sets RAILWAY_ENVIRONMENT automatically; use it to detect production
    RAILWAY_ENVIRONMENT: Optional[str] = Field(default=None, description="Auto-set by Railway")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")

    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production (explicit ENVIRONMENT or Railway production)."""
        return self.ENVIRONMENT == "production" or self.RAILWAY_ENVIRONMENT == "production"

    # Database Configuration
    # Railway provides DATABASE_URL directly; use it if available, otherwise construct from components
    DATABASE_URL_PROVIDED: Optional[str] = Field(
        default=None,
        validation_alias="DATABASE_URL",
        description="Full database URL (auto-provided by Railway or other platforms)",
    )
    POSTGRES_SERVER: str = Field(default="localhost", description="PostgreSQL server host")
    POSTGRES_USER: str = Field(default="postgres", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="", description="PostgreSQL password")
    POSTGRES_DB: str = Field(default="cat_food_research", description="PostgreSQL database name")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        Get database URL. Prefers Railway's provided DATABASE_URL, falls back to constructed URL.
        Converts postgres:// to postgresql+asyncpg:// for SQLAlchemy async support.
        """
        if self.DATABASE_URL_PROVIDED:
            # Railway provides postgres:// but we need postgresql+asyncpg://
            url = self.DATABASE_URL_PROVIDED
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        # Construct from components (local development)
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Security - CRITICAL: Must be set in production
    # NOTE: We allow this to be empty in local/dev scripts so DB tooling can run without auth setup.
    # In production, we validate this is set at app startup.
    SECRET_KEY: str = Field(
        default="",
        description="Secret key for JWT tokens. REQUIRED in production via environment variable. Generate with: openssl rand -hex 32",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration in minutes")

    # Vector Database (Qdrant)
    QDRANT_HOST: str = Field(default="localhost", description="Qdrant server host or Qdrant Cloud URL")
    QDRANT_PORT: int = Field(default=6333, description="Qdrant server port")
    QDRANT_API_KEY: Optional[str] = Field(default=None, description="Qdrant API Key - REQUIRED for Qdrant Cloud")

    # AI Services - CRITICAL: Must be set via environment variables
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, description="OpenAI API Key - REQUIRED if using OpenAI services"
    )

    # NOTE: Optional for local/dev scripts; required only when AI features are used (and in production startup).
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API Key")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=10, description="Default requests per minute per IP")
    RATE_LIMIT_SEARCH_PER_MINUTE: int = Field(
        default=10, description="Search endpoint requests per minute per IP (stricter due to LLM costs)"
    )
    RATE_LIMIT_ADMIN_PER_MINUTE: int = Field(default=30, description="Admin endpoints requests per minute per IP")

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields in .env file
    )


settings = Settings()
