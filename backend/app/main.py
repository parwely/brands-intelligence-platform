# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .core.database import get_db
from .core.config import settings
from .models.brand import Brand
from .models.mention import Mention
from .services.ml_service import ml_service
from typing import List
from pydantic import BaseModel
import uuid

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models for ML
class TextAnalysisRequest(BaseModel):
    text: str

class TextAnalysisResponse(BaseModel):
    sentiment_score: float
    sentiment_label: str
    confidence: float
    crisis_probability: float
    urgency_score: float
    crisis_indicators: int
    model_info: dict

class MentionReanalysisResponse(BaseModel):
    mention_id: str
    old_sentiment: float
    new_sentiment: float
    old_crisis_probability: float
    new_crisis_probability: float
    analysis: dict

# Existing endpoints
@app.get("/")
async def root():
    return {"message": "Brand Intelligence Platform API", "version": settings.version}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name}

@app.get("/api/brands")
async def get_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Brand))
    brands = result.scalars().all()
    return [{"id": brand.id, "name": brand.name, "industry": brand.industry} for brand in brands]

@app.get("/api/mentions")
async def get_mentions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Mention).limit(10))
    mentions = result.scalars().all()
    return [{"id": mention.id, "content": mention.content, "platform": mention.platform, "sentiment_score": mention.sentiment_score} for mention in mentions]

@app.get("/api/demo/sample-data")
async def get_sample_data(db: AsyncSession = Depends(get_db)):
    # Get brands
    brands_result = await db.execute(select(Brand))
    brands = brands_result.scalars().all()
    
    # Get mentions
    mentions_result = await db.execute(select(Mention).limit(5))
    mentions = mentions_result.scalars().all()
    
    return {
        "brands": [{"id": b.id, "name": b.name, "industry": b.industry} for b in brands],
        "mentions": [{"id": m.id, "content": m.content, "sentiment_score": m.sentiment_score} for m in mentions],
        "message": "Sample data loaded successfully!"
    }

# NEW ML ENDPOINTS
@app.post("/api/ml/analyze-sentiment", response_model=TextAnalysisResponse)
async def analyze_sentiment(request: TextAnalysisRequest):
    """Analyze sentiment of provided text using ML pipeline"""
    try:
        result = await ml_service.analyze_mention_sentiment(request.text)
        return TextAnalysisResponse(
            sentiment_score=result['sentiment_score'],
            sentiment_label=result['sentiment_label'],
            confidence=result['confidence'],
            crisis_probability=result['crisis_probability'],
            urgency_score=result['urgency_score'],
            crisis_indicators=result['crisis_indicators'],
            model_info=result['model_info']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML analysis failed: {str(e)}")

@app.post("/api/ml/batch-analyze")
async def batch_analyze_sentiments(texts: List[str]):
    """Analyze multiple texts at once"""
    try:
        results = await ml_service.batch_analyze_mentions(texts)
        return {
            "total_analyzed": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.post("/api/mentions/{mention_id}/reanalyze", response_model=MentionReanalysisResponse)
async def reanalyze_mention(mention_id: str, db: AsyncSession = Depends(get_db)):
    """Re-analyze existing mention with updated ML models"""
    try:
        # Get mention
        result = await db.execute(select(Mention).where(Mention.id == mention_id))
        mention = result.scalar_one_or_none()
        
        if not mention:
            raise HTTPException(status_code=404, detail="Mention not found")
        
        # Store old values
        old_sentiment = mention.sentiment_score
        old_crisis_probability = mention.crisis_probability
        
        # Analyze with ML
        analysis = await ml_service.analyze_mention_sentiment(mention.content)
        
        # Update mention
        mention.sentiment_score = analysis['sentiment_score']
        mention.sentiment_label = analysis['sentiment_label']
        mention.crisis_probability = analysis['crisis_probability']
        
        await db.commit()
        await db.refresh(mention)
        
        return MentionReanalysisResponse(
            mention_id=mention_id,
            old_sentiment=old_sentiment,
            new_sentiment=mention.sentiment_score,
            old_crisis_probability=old_crisis_probability,
            new_crisis_probability=mention.crisis_probability,
            analysis=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reanalysis failed: {str(e)}")

@app.get("/api/analytics/sentiment-overview")
async def sentiment_overview(db: AsyncSession = Depends(get_db)):
    """Get comprehensive sentiment analytics for dashboard"""
    try:
        result = await db.execute(select(Mention))
        mentions = result.scalars().all()
        
        if not mentions:
            return {"total_mentions": 0, "sentiment_breakdown": {}}
        
        # Calculate sentiment breakdown
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        total_sentiment = 0
        high_crisis_count = 0
        urgent_mentions = 0
        
        for mention in mentions:
            sentiment_counts[mention.sentiment_label] += 1
            total_sentiment += mention.sentiment_score
            if mention.crisis_probability > 0.7:
                high_crisis_count += 1
            # Calculate urgency on the fly for existing mentions
            if mention.sentiment_score < 0.3 or mention.crisis_probability > 0.5:
                urgent_mentions += 1
        
        avg_sentiment = total_sentiment / len(mentions)
        
        return {
            "total_mentions": len(mentions),
            "average_sentiment": round(avg_sentiment, 3),
            "sentiment_breakdown": sentiment_counts,
            "high_crisis_alerts": high_crisis_count,
            "urgent_mentions": urgent_mentions,
            "sentiment_distribution": {
                "positive_percentage": round((sentiment_counts["positive"] / len(mentions)) * 100, 1),
                "negative_percentage": round((sentiment_counts["negative"] / len(mentions)) * 100, 1),
                "neutral_percentage": round((sentiment_counts["neutral"] / len(mentions)) * 100, 1)
            },
            "crisis_metrics": {
                "crisis_percentage": round((high_crisis_count / len(mentions)) * 100, 1),
                "urgent_percentage": round((urgent_mentions / len(mentions)) * 100, 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@app.get("/api/ml/model-info")
async def get_model_info():
    """Get information about loaded ML models"""
    try:
        return await ml_service.get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model info failed: {str(e)}")

@app.get("/api/mentions/crisis-alerts")
async def get_crisis_alerts(
    threshold: float = 0.7,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get mentions with high crisis probability"""
    try:
        result = await db.execute(
            select(Mention)
            .where(Mention.crisis_probability >= threshold)
            .order_by(Mention.crisis_probability.desc(), Mention.published_at.desc())
            .limit(limit)
        )
        mentions = result.scalars().all()
        
        return {
            "crisis_alerts": [
                {
                    "id": mention.id,
                    "brand_id": mention.brand_id,
                    "content": mention.content,
                    "platform": mention.platform,
                    "sentiment_score": mention.sentiment_score,
                    "sentiment_label": mention.sentiment_label,
                    "crisis_probability": mention.crisis_probability,
                    "published_at": mention.published_at.isoformat(),
                    "urgency_level": "HIGH" if mention.crisis_probability > 0.8 else "MEDIUM"
                }
                for mention in mentions
            ],
            "total_alerts": len(mentions),
            "threshold": threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crisis alerts failed: {str(e)}")