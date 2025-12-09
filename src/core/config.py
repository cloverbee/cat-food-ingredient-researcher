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
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")

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
    SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT tokens - REQUIRED via environment variable. Generate with: openssl rand -hex 32",
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

    GEMINI_API_KEY: str = Field(..., description="Google Gemini API Key - REQUIRED via environment variable")

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields in .env file
    )


settings = Settings()
