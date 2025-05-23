# backend/app/core/init_db.py
from sqlalchemy.ext.asyncio import AsyncSession
from .database import engine, Base
import logging

logger = logging.getLogger(__name__)

async def init_database():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise