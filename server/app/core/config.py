import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    SNOWFLAKE_USER: str
    SNOWFLAKE_PASSWORD: str
    SNOWFLAKE_ACCOUNT: str
    SNOWFLAKE_WAREHOUSE: str
    SNOWFLAKE_DATABASE: str
    SNOWFLAKE_SCHEMA: str
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Clerk Authentication
    CLERK_PUBLISHABLE_KEY: Optional[str] = None
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_FRONTEND_API: Optional[str] = None  # e.g., "your-domain.clerk.accounts.dev"
    
    # CORS Settings
    CORS_ORIGINS: str = "*"  # Comma-separated list: "http://localhost:3000,https://yourdomain.com"
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Application settings
    APP_NAME: str = "Second Brain"
    DEBUG: bool = False
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> list:
        """Parse CORS origins into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()