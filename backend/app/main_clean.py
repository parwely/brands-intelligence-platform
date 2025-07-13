# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .core.database import get_db
from .core.config import settings
from .models.brand import Brand
from .models.mention import Mention
from typing import List
from pydantic import BaseModel
import uuid

# Import API routers
from .api import brands, mentions, analytics, demo
from .api.ml import router as ml_router

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

# Include API routers
app.include_router(brands.router)
app.include_router(mentions.router)
app.include_router(analytics.router)
app.include_router(demo.router)
app.include_router(ml_router)

# Basic health check
@app.get("/")
async def read_root():
    return {
        "message": "Brand Intelligence Platform API",
        "version": settings.version,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.version,
        "database": "connected",
        "ml_service": "available"
    }

# Basic data endpoints
@app.get("/api/brands")
async def get_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Brand).limit(10))
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
