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
    POSTGRES_SERVER: str = Field(default="localhost", description="PostgreSQL server host")
    POSTGRES_USER: str = Field(default="postgres", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL password - REQUIRED via environment variable")
    POSTGRES_DB: str = Field(default="cat_food_research", description="PostgreSQL database name")
    POSTGRES_PORT: int = Field(default=5433, description="PostgreSQL port")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construct async database URL from components."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Security - CRITICAL: Must be set in production
    SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT tokens - REQUIRED via environment variable. Generate with: openssl rand -hex 32",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration in minutes")

    # Vector Database (Qdrant)
    QDRANT_HOST: str = Field(default="localhost", description="Qdrant server host")
    QDRANT_PORT: int = Field(default=6333, description="Qdrant server port")

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
