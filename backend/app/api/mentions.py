# backend/app/api/mentions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from ..core.database import get_db
from ..models.mention import Mention
from ..schemas.mention import Mention as MentionSchema

router = APIRouter()

@router.get("/", response_model=List[MentionSchema])
async def get_mentions(
    brand_id: Optional[uuid.UUID] = None,
    platform: Optional[str] = None,
    days: int = Query(7, description="Number of days to look back"),
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get mentions with filtering options"""
    
    # Build query conditions
    conditions = []
    
    if brand_id:
        conditions.append(Mention.brand_id == brand_id)
    
    if platform:
        conditions.append(Mention.platform == platform)
    
    # Date filter
    date_threshold = datetime.utcnow() - timedelta(days=days)
    conditions.append(Mention.published_at >= date_threshold)
    
    # Execute query
    query = select(Mention).where(and_(*conditions)).limit(limit).order_by(Mention.published_at.desc())
    result = await db.execute(query)
    mentions = result.scalars().all()
    
    return mentions

@router.get("/crisis-alerts", response_model=List[MentionSchema])
async def get_crisis_alerts(
    brand_id: Optional[uuid.UUID] = None,
    threshold: float = Query(0.7, description="Crisis probability threshold"),
    db: AsyncSession = Depends(get_db)
):
    """Get high-risk mentions that might indicate a crisis"""
    
    conditions = [Mention.crisis_probability >= threshold]
    
    if brand_id:
        conditions.append(Mention.brand_id == brand_id)
    
    query = select(Mention).where(and_(*conditions)).order_by(Mention.crisis_probability.desc()).limit(50)
    result = await db.execute(query)
    mentions = result.scalars().all()
    
    return mentions

@router.get("/analytics/sentiment-trend")
async def get_sentiment_trend(
    brand_id: uuid.UUID,
    days: int = Query(30),
    db: AsyncSession = Depends(get_db)
):
    """Get sentiment trend over time"""
    
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    # This would normally use ClickHouse for better performance
    # For now, simple PostgreSQL aggregation
    query = select(Mention).where(
        and_(
            Mention.brand_id == brand_id,
            Mention.published_at >= date_threshold,
            Mention.sentiment_score.isnot(None)
        )
    ).order_by(Mention.published_at)
    
    result = await db.execute(query)
    mentions = result.scalars().all()
    
    # Group by day and calculate average sentiment
    daily_sentiment = {}
    for mention in mentions:
        day = mention.published_at.date()
        if day not in daily_sentiment:
            daily_sentiment[day] = []
        daily_sentiment[day].append(mention.sentiment_score)
    
    # Calculate averages
    trend_data = []
    for day, scores in daily_sentiment.items():
        avg_sentiment = sum(scores) / len(scores)
        trend_data.append({
            "date": day.isoformat(),
            "sentiment": avg_sentiment,
            "mention_count": len(scores)
        })
    
    return {"trend": sorted(trend_data, key=lambda x: x["date"])}

@router.get("/{mention_id}", response_model=MentionSchema)
async def get_mention(
    mention_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get specific mention details"""
    result = await db.execute(select(Mention).where(Mention.id == mention_id))
    mention = result.scalar_one_or_none()
    
    if not mention:
        raise HTTPException(status_code=404, detail="Mention not found")
    
    return mention