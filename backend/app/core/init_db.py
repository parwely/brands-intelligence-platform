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
    """Create sample data with real ML analysis"""
    try:
        # Import ML service here to avoid circular imports
        from ..services.ml_service import ml_service
        
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
            await session.refresh(brands[0])  # Ensure we have the IDs
            logger.info(f"Sample brands created: {len(brands)}")
            
            # Create diverse, realistic sample mentions with ML analysis
            mention_templates = [
                # TechCorp mentions
                ("Amazing product! TechCorp's latest AI solution revolutionized our workflow. Incredible technology! 🚀", "Twitter"),
                ("TechCorp's customer service is TERRIBLE! My issue hasn't been resolved for weeks. This is unacceptable!!!", "Twitter"),
                ("TechCorp is okay. The software works but the interface could be more intuitive.", "Reddit"),
                ("URGENT: TechCorp charged my card twice for the same subscription! This needs immediate attention!", "Facebook"),
                
                # GreenEnergy mentions  
                ("Love GreenEnergy's commitment to sustainability! Their solar panels are fantastic quality 🌱", "Instagram"),
                ("GreenEnergy's installation was a disaster. Workers were unprofessional and left a mess.", "Google Reviews"),
                ("GreenEnergy prices are reasonable compared to competitors. Good value for money.", "Twitter"),
                ("WARNING: GreenEnergy made false claims about energy savings! Considering legal action.", "Reddit"),
                
                # HealthPlus mentions
                ("HealthPlus saved my life! The medical team was incredible and the technology is cutting-edge 💙", "Facebook"),
                ("HealthPlus appointment system is broken again. Can't book anything online. So frustrating!", "Twitter"),
                ("HealthPlus is decent. Good doctors but the wait times are pretty long.", "Google Reviews"),
                ("SCAM ALERT! HealthPlus is billing for services never received. Fraud investigation needed!", "Reddit")
            ]
            
            all_mentions = []
            for i, brand in enumerate(brands):
                # Get mentions for this brand (4 mentions per brand)
                brand_mentions = mention_templates[i*4:(i+1)*4]
                
                for j, (content, platform) in enumerate(brand_mentions):
                    # Analyze with ML pipeline
                    logger.info(f"Analyzing mention: {content[:50]}...")
                    analysis = await ml_service.analyze_mention_sentiment(content)
                    
                    mention = Mention(
                        id=str(uuid.uuid4()),
                        brand_id=brand.id,
                        content=content,
                        platform=platform,
                        sentiment_score=analysis['sentiment_score'],
                        sentiment_label=analysis['sentiment_label'],
                        crisis_probability=analysis['crisis_probability'],
                        published_at=datetime.utcnow() - timedelta(hours=j * 6, minutes=j * 15),
                        likes_count=max(1, int(analysis['sentiment_score'] * 50) + j * 10),
                        shares_count=max(0, int(analysis['sentiment_score'] * 20) + j * 2),
                        comments_count=max(0, int(analysis['urgency_score'] * 15) + j)
                    )
                    all_mentions.append(mention)
                    
                    logger.info(f"Created mention: sentiment={analysis['sentiment_label']} ({analysis['sentiment_score']:.3f}), crisis={analysis['crisis_probability']:.3f}")
            
            # Add all mentions to session
            for mention in all_mentions:
                session.add(mention)
            
            await session.commit()
            logger.info(f"Sample mentions created with ML analysis: {len(all_mentions)}")
            
            # Log summary statistics
            positive_count = sum(1 for m in all_mentions if m.sentiment_label == 'positive')
            negative_count = sum(1 for m in all_mentions if m.sentiment_label == 'negative')
            neutral_count = sum(1 for m in all_mentions if m.sentiment_label == 'neutral')
            crisis_count = sum(1 for m in all_mentions if m.crisis_probability > 0.7)
            
            logger.info(f"ML Analysis Summary:")
            logger.info(f"  Positive: {positive_count}, Negative: {negative_count}, Neutral: {neutral_count}")
            logger.info(f"  High Crisis Risk: {crisis_count}")
            
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