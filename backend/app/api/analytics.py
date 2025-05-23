from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid

from ..core.database import get_db
from ..models.mention import Mention

router = APIRouter()

@router.get("/sentiment-overview")
async def get_sentiment_overview(
    brand_id: uuid.UUID,
    days: int = Query(7, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get sentiment analysis overview for a brand"""
    
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    # Get sentiment distribution
    query = select(
        Mention.sentiment_label,
        func.count(Mention.id).label('count'),
        func.avg(Mention.sentiment_score).label('avg_score')
    ).where(
        Mention.brand_id == brand_id,
        Mention.published_at >= date_threshold
    ).group_by(Mention.sentiment_label)
    
    result = await db.execute(query)
    sentiment_data = result.all()
    
    return {
        "brand_id": brand_id,
        "period_days": days,
        "sentiment_distribution": [
            {
                "sentiment": row.sentiment_label,
                "count": row.count,
                "average_score": float(row.avg_score) if row.avg_score else 0
            }
            for row in sentiment_data
        ]
    }

@router.get("/platform-breakdown")
async def get_platform_breakdown(
    brand_id: uuid.UUID,
    days: int = Query(30),
    db: AsyncSession = Depends(get_db)
):
    """Get mention distribution by platform"""
    
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    query = select(
        Mention.platform,
        func.count(Mention.id).label('mention_count'),
        func.avg(Mention.sentiment_score).label('avg_sentiment'),
        func.sum(Mention.likes_count + Mention.shares_count + Mention.comments_count).label('total_engagement')
    ).where(
        Mention.brand_id == brand_id,
        Mention.published_at >= date_threshold
    ).group_by(Mention.platform)
    
    result = await db.execute(query)
    platform_data = result.all()
    
    return {
        "brand_id": brand_id,
        "platforms": [
            {
                "platform": row.platform,
                "mention_count": row.mention_count,
                "avg_sentiment": float(row.avg_sentiment) if row.avg_sentiment else 0,
                "total_engagement": row.total_engagement or 0
            }
            for row in platform_data
        ]
    }


@router.get("/crisis-metrics")
async def get_crisis_metrics(
    brand_id: uuid.UUID,
    threshold: float = Query(0.7, description="Crisis probability threshold"),
    db: AsyncSession = Depends(get_db)
):
    """Get crisis detection metrics"""
    
    # Get recent high-risk mentions
    query = select(func.count(Mention.id)).where(
        Mention.brand_id == brand_id,
        Mention.crisis_probability >= threshold,
        Mention.published_at >= datetime.utcnow() - timedelta(hours=24)
    )
    
    result = await db.execute(query)
    crisis_count = result.scalar() or 0  # Handle None case
    
    return {
        "brand_id": brand_id,
        "crisis_alerts_24h": crisis_count,
        "threshold": threshold,
        "status": "high_risk" if crisis_count > 5 else "normal"
    }