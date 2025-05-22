# backend/app/core/database.py - Production Ready Version
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
import redis.asyncio as redis
from elasticsearch import AsyncElasticsearch
from clickhouse_driver import Client
import logging
from .config import settings

logger = logging.getLogger(__name__)

# PostgreSQL (Main Database)
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # SQL logging in debug mode
    pool_size=20,
    max_overflow=0
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Redis (Async version for better performance)
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

# Elasticsearch
es_client = AsyncElasticsearch([settings.elasticsearch_url])

# ClickHouse
clickhouse_client = Client.from_url(settings.clickhouse_url)

# Database Dependency with proper error handling
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

# Health check functions
async def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False