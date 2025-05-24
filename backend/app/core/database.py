# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator, Optional, Union
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Create engine with SQLite-compatible settings
if "sqlite" in settings.database_url.lower():
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=20,
        max_overflow=0
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Optional services with specific types
redis_client = None  # Will be redis.Redis or None
es_client = None     # Will be AsyncElasticsearch or None  
clickhouse_client = None  # Will be Client or None

if settings.use_redis:
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        logger.info("Redis client initialized")
    except Exception as e:
        logger.warning(f"Redis not available: {e}")

try:
    from elasticsearch import AsyncElasticsearch
    es_client = AsyncElasticsearch([settings.elasticsearch_url])
    logger.info("Elasticsearch client initialized")
except Exception as e:
    logger.warning(f"Elasticsearch not available: {e}")

try:
    from clickhouse_driver import Client
    clickhouse_client = Client.from_url(settings.clickhouse_url)
    logger.info("ClickHouse client initialized")
except Exception as e:
    logger.warning(f"ClickHouse not available: {e}")

# Database Dependency
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

# Health check function
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