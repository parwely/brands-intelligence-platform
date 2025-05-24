# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .core.database import get_db
from .core.config import settings
from .models.brand import Brand
from .models.mention import Mention
from sqlalchemy import select

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