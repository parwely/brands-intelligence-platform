# backend/app/api/demo.py
from fastapi import APIRouter
from typing import Dict, Any
import uuid
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/sample-data")
async def get_sample_data() -> Dict[str, Any]:
    """Generate sample demo data for testing"""
    
    # Sample brand
    brand_id = str(uuid.uuid4())
    
    # Sample mentions
    platforms = ["twitter", "facebook", "instagram", "reddit", "news"]
    sentiments = ["positive", "neutral", "negative"]
    
    sample_mentions = []
    for i in range(20):
        sample_mentions.append({
            "id": str(uuid.uuid4()),
            "brand_id": brand_id,
            "content": f"Sample mention {i+1} about the brand",
            "platform": random.choice(platforms),
            "sentiment_label": random.choice(sentiments),
            "sentiment_score": round(random.uniform(-1, 1), 2),
            "crisis_probability": round(random.uniform(0, 1), 2),
            "published_at": (datetime.utcnow() - timedelta(days=random.randint(0, 7))).isoformat(),
            "likes_count": random.randint(0, 100),
            "shares_count": random.randint(0, 50),
            "comments_count": random.randint(0, 25)
        })
    
    return {
        "brand": {
            "id": brand_id,
            "name": "Demo Brand",
            "industry": "Technology"
        },
        "mentions": sample_mentions,
        "analytics": {
            "total_mentions": len(sample_mentions),
            "sentiment_breakdown": {
                "positive": len([m for m in sample_mentions if m["sentiment_label"] == "positive"]),
                "neutral": len([m for m in sample_mentions if m["sentiment_label"] == "neutral"]),
                "negative": len([m for m in sample_mentions if m["sentiment_label"] == "negative"])
            }
        }
    }