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
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Application settings
    APP_NAME: str = "Second Brain"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()