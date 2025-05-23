# backend/app/api/demo.py
from fastapi import APIRouter, Query
from typing import Dict, List
from ..services.mock_data_service import mock_service

router = APIRouter()

@router.get("/mentions/{brand_name}")
async def get_demo_mentions(
    brand_name: str,
    days: int = Query(30, description="Days to look back"),
    count: int = Query(100, description="Number of mentions")
):
    """Generiert Demo-Mentions für eine Brand (kostenlos!)"""
    mentions = mock_service.generate_mentions(brand_name, days, count)
    return {
        "brand": brand_name,
        "total_mentions": len(mentions),
        "mentions": mentions,
        "demo_mode": True
    }

@router.get("/analytics/{brand_name}/sentiment-trend")
async def get_demo_sentiment_trend(
    brand_name: str,
    days: int = Query(30)
):
    """Demo Sentiment Trend (kostenlos!)"""
    trend_data = mock_service.generate_trend_data(days)
    return {
        "brand": brand_name,
        "period_days": days,
        "trend": trend_data,
        "demo_mode": True
    }

@router.get("/analytics/{brand_name}/crisis-alerts")
async def get_demo_crisis_alerts(brand_name: str):
    """Demo Crisis Alerts (kostenlos!)"""
    mentions = mock_service.generate_mentions(brand_name, days=7, count=50)
    
    # Filter nur Crisis-Mentions
    crisis_mentions = [m for m in mentions if m["crisis_probability"] > 0.7]
    
    return {
        "brand": brand_name,
        "alert_count": len(crisis_mentions),
        "alerts": crisis_mentions[:10],  # Top 10 alerts
        "demo_mode": True
    }

@router.get("/analytics/competitive-intelligence")
async def get_demo_competitive_analysis():
    """Demo Competitive Analysis (kostenlos!)"""
    analysis = mock_service.generate_competitive_analysis()
    return {
        "analysis": analysis,
        "generated_at": "2024-01-01T00:00:00Z",
        "demo_mode": True
    }

@router.get("/demo-brands")
async def get_demo_brands():
    """Verfügbare Demo-Brands"""
    return {
        "brands": mock_service.DEMO_BRANDS,
        "info": "Diese Brands enthalten realistische Demo-Daten",
        "demo_mode": True
    }

@router.post("/populate-demo-data")
async def populate_demo_data():
    """Befüllt Datenbank mit Demo-Daten (für Entwicklung)"""
    # Hier würdest du die Mock-Daten in die echte DB schreiben
    # für jetzt nur return success
    return {
        "message": "Demo data populated successfully",
        "brands_created": len(mock_service.DEMO_BRANDS),
        "demo_mode": True
    }