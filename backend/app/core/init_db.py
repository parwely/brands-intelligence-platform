# backend/app/core/init_db.py
import logging
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import engine, Base, AsyncSessionLocal
from ..models.brand import Brand
from ..models.mention import Mention
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def create_tables():
    """Create all database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

async def create_sample_data():
    """Create sample data for development"""
    try:
        async with AsyncSessionLocal() as session:
            # Check if data already exists
            result = await session.execute(select(Brand).limit(1))
            if result.scalar_one_or_none():
                logger.info("Sample data already exists")
                return
            
            # Create sample brands
            brands = [
                Brand(
                    id=str(uuid.uuid4()),
                    name="TechCorp", 
                    industry="Technology", 
                    website="https://techcorp.com",
                    is_active=True
                ),
                Brand(
                    id=str(uuid.uuid4()),
                    name="GreenEnergy", 
                    industry="Energy", 
                    website="https://greenenergy.com",
                    is_active=True
                ),
                Brand(
                    id=str(uuid.uuid4()),
                    name="HealthPlus", 
                    industry="Healthcare", 
                    website="https://healthplus.com",
                    is_active=True
                )
            ]
            
            for brand in brands:
                session.add(brand)
            
            await session.commit()
            await session.refresh(brands[0])  # Refresh to get the ID
            logger.info(f"Sample brands created: {len(brands)}")
            
            # Create sample mentions for each brand
            all_mentions = []
            for i, brand in enumerate(brands):
                mentions = [
                    Mention(
                        id=str(uuid.uuid4()),
                        brand_id=brand.id,
                        content=f"Great experience with {brand.name}! Highly recommend their services.",
                        platform="Twitter",
                        sentiment_score=0.8,
                        sentiment_label="positive",
                        crisis_probability=0.1,
                        published_at=datetime.utcnow() - timedelta(hours=j),
                        likes_count=25 + j * 5,
                        shares_count=5 + j,
                        comments_count=3 + j
                    ) for j in range(3)
                ]
                all_mentions.extend(mentions)
            
            for mention in all_mentions:
                session.add(mention)
            
            await session.commit()
            logger.info(f"Sample mentions created: {len(all_mentions)}")
            
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        raise

async def init_database():
    """Initialize database with tables and sample data"""
    try:
        logger.info("Starting database initialization...")
        await create_tables()
        await create_sample_data()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())