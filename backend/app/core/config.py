# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Brand Intelligence Platform"
    version: str = "1.0.0"
    debug: bool = True
    
    # Required fields with defaults for development
    secret_key: str = "default-dev-secret-key-change-in-production"
    database_url: str = "sqlite+aiosqlite:///./brand_intelligence.db"
    
    # Optional services
    redis_url: str = "redis://localhost:6379/0"
    elasticsearch_url: str = "http://localhost:9200"
    clickhouse_url: str = "http://localhost:8123"
    use_redis: bool = True
    
    # API Keys
    news_api_key: str = ""
    googlenews_query: str = ""
    
    # ML Models
    sentiment_model_path: str = "./ml/models/sentiment_model"
    crisis_model_path: str = "./ml/models/crisis_model"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()