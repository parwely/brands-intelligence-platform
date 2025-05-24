# backend/app/core/init_db.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select  # Add this import
from .database import engine, Base, AsyncSessionLocal
from ..models.brand import Brand
from ..models.mention import Mention
import logging
import uuid

logger = logging.getLogger(__name__)

async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

async def create_sample_data():
    """Create sample data for development"""
    async with AsyncSessionLocal() as session:
        # Check if data already exists
        result = await session.execute(select(Brand).limit(1))
        if result.scalar_one_or_none():
            logger.info("Sample data already exists")
            return
        
        # Create sample brands
        brands = [
            Brand(name="TechCorp", industry="Technology", website="https://techcorp.com"),
            Brand(name="GreenEnergy", industry="Energy", website="https://greenenergy.com"),
            Brand(name="HealthPlus", industry="Healthcare", website="https://healthplus.com")
        ]
        
        for brand in brands:
            session.add(brand)
        
        await session.commit()
        logger.info("Sample brands created")

async def init_database():
    """Initialize database with tables and sample data"""
    try:
        await create_tables()
        await create_sample_data()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise