# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    app_name: str = "Brand Intelligence Platform"
    debug: bool = False
    version: str = "0.1.0"
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/brand_intelligence"
    clickhouse_url: str = "clickhouse://localhost:9000/default"
    redis_url: str = "redis://localhost:6379"
    elasticsearch_url: str = "http://localhost:9200"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Keys
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    news_api_key: Optional[str] = None
    
    # ML Models
    sentiment_model_path: str = "./ml/models/sentiment_model"
    crisis_model_path: str = "./ml/models/crisis_model"
    
    class Config:
        env_file = ".env"

settings = Settings()