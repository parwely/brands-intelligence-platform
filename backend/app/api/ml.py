# backend/app/api/ml.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional
import asyncio
import json
import logging
from datetime import datetime, timedelta
from ..services.ml_service import MLService
from ..core.database import get_db
from ..models.mention import Mention
from ..schemas.mention import MentionCreate, Mention as MentionSchema
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ML Analytics"])

# Initialize ML service as singleton
ml_service = MLService()

@router.get("/status")
async def get_ml_service_status():
    """Get the status of all ML service components"""
    try:
        status = ml_service.get_service_status()
        return {
            "status": "healthy" if status.get("service_healthy") else "degraded",
            "components": status,
            "message": "All ML components operational" if status.get("service_healthy") 
                      else "Some ML components unavailable"
        }
    except Exception as e:
        logger.error(f"Failed to get ML service status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ML service status")

@router.post("/analyze/sentiment")
async def analyze_sentiment(data: Dict):
    """Analyze sentiment of a single text"""
    try:
        text = data.get("text", "")
        use_bert = data.get("use_bert", True)
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = await ml_service.analyze_mention_sentiment(text, use_bert=use_bert)
        return {
            "success": True,
            "data": result,
            "processing_time": result.get("processing_time_ms", 0)
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Sentiment analysis failed")

@router.post("/analyze/crisis")
async def analyze_crisis(data: Dict):
    """Analyze crisis indicators in mentions for a brand"""
    try:
        mentions = data.get("mentions", [])
        brand_name = data.get("brand_name", "")
        
        if not mentions or not brand_name:
            raise HTTPException(status_code=400, detail="Mentions and brand_name are required")
        
        result = await ml_service.analyze_crisis(mentions, brand_name)
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Crisis analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Crisis analysis failed")

@router.post("/analyze/brand-health")
async def analyze_brand_health(data: Dict):
    """Comprehensive brand health analysis"""
    try:
        brand_name = data.get("brand_name", "")
        mentions = data.get("mentions", [])
        time_window_hours = data.get("time_window_hours", 24)
        
        if not brand_name:
            raise HTTPException(status_code=400, detail="brand_name is required")
        
        result = await ml_service.analyze_brand_health(brand_name, mentions, time_window_hours)
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Brand health analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Brand health analysis failed")

@router.post("/analyze/batch")
async def batch_analyze_mentions(data: Dict):
    """Analyze multiple mentions for sentiment and crisis indicators"""
    try:
        mentions = data.get("mentions", [])
        brand_name = data.get("brand_name", "")
        include_bert = data.get("include_bert", True)
        
        if not mentions or not brand_name:
            raise HTTPException(status_code=400, detail="Mentions and brand_name are required")
        
        result = await ml_service.batch_analyze_mentions(mentions, brand_name, include_bert)
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Batch analysis failed")

@router.get("/analyze/realtime/{brand_name}")
async def realtime_brand_analysis(brand_name: str, db: Session = Depends(get_db)):
    """Real-time streaming analysis for a brand"""
    try:
        async def generate_analysis():
            """Generate real-time analysis stream"""
            while True:
                try:
                    # Fetch recent mentions from database
                    recent_mentions = db.query(Mention)\
                        .filter(Mention.brand_id == brand_name)\
                        .filter(Mention.created_at >= datetime.now() - timedelta(hours=1))\
                        .limit(50)\
                        .all()
                    
                    if recent_mentions:
                        # Convert to dict format
                        mention_data = [
                            {
                                "id": str(mention.id),
                                "text": mention.content,
                                "source": mention.source,
                                "timestamp": mention.created_at.isoformat()
                            }
                            for mention in recent_mentions
                        ]
                        
                        # Perform analysis
                        analysis = await ml_service.analyze_brand_health(brand_name, mention_data)
                        
                        # Stream result
                        yield f"data: {json.dumps(analysis)}\n\n"
                    
                    await asyncio.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Realtime analysis error: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    await asyncio.sleep(60)  # Wait longer on error
        
        return StreamingResponse(
            generate_analysis(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        logger.error(f"Realtime analysis setup failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to setup realtime analysis")

@router.post("/process/mention")
async def process_new_mention(
    mention_data: Dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process a new mention through the ML pipeline"""
    try:
        text = mention_data.get("text", "")
        brand_name = mention_data.get("brand_name", "")
        source = mention_data.get("source", "unknown")
        
        if not text or not brand_name:
            raise HTTPException(status_code=400, detail="text and brand_name are required")
        
        # Quick sentiment analysis for immediate response
        sentiment_result = await ml_service.analyze_mention_sentiment(text, use_bert=False)
        
        # Add background processing for full analysis
        background_tasks.add_task(
            process_mention_background,
            mention_data,
            db
        )
        
        return {
            "success": True,
            "mention_id": mention_data.get("id", "generated"),
            "quick_sentiment": sentiment_result.get("final_sentiment", {}),
            "message": "Mention processed, full analysis in progress"
        }
        
    except Exception as e:
        logger.error(f"Mention processing failed: {e}")
        raise HTTPException(status_code=500, detail="Mention processing failed")

async def process_mention_background(mention_data: Dict, db: Session):
    """Background task for full mention processing"""
    try:
        text = mention_data.get("text", "")
        brand_name = mention_data.get("brand_name", "")
        
        # Full sentiment analysis with BERT
        sentiment_result = await ml_service.analyze_mention_sentiment(text, use_bert=True)
        
        # Crisis detection
        crisis_result = await ml_service.analyze_crisis([mention_data], brand_name)
        
        # Store results in database (simplified)
        # In a real implementation, you'd store these results properly
        logger.info(f"Background analysis completed for mention: {mention_data.get('id')}")
        logger.info(f"Sentiment: {sentiment_result.get('final_sentiment', {}).get('sentiment_label')}")
        logger.info(f"Crisis Level: {crisis_result.get('overall_crisis_level')}")
        
    except Exception as e:
        logger.error(f"Background mention processing failed: {e}")

@router.get("/test/demo")
async def demo_ml_analysis():
    """Demo endpoint showing ML capabilities"""
    try:
        # Demo data
        demo_mentions = [
            {
                "id": "demo_1",
                "text": "I absolutely love this brand! Amazing quality and customer service.",
                "source": "twitter",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "demo_2", 
                "text": "This product is terrible and dangerous! Major safety issues reported.",
                "source": "facebook",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "demo_3",
                "text": "Lawsuit filed against company for fraud and data breach!",
                "source": "news",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Perform comprehensive analysis
        analysis_result = await ml_service.analyze_brand_health("DemoBrand", demo_mentions)
        
        return {
            "success": True,
            "demo_data": demo_mentions,
            "analysis": analysis_result,
            "message": "Demo analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Demo analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Demo analysis failed")

@router.post("/extract/features")
async def extract_text_features(data: Dict):
    """Extract features from text for analysis"""
    try:
        text = data.get("text", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        features = await ml_service.extract_features(text)
        return {
            "success": True,
            "features": features,
            "text_length": len(text)
        }
        
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Feature extraction failed")
