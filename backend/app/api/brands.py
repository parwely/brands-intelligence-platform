# backend/app/api/brands.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from ..core.database import get_db
from ..models.brand import Brand
from ..schemas.brand import Brand as BrandSchema, BrandCreate

router = APIRouter()

@router.get("/", response_model=List[BrandSchema])
async def get_brands(db: AsyncSession = Depends(get_db)):
    """Get all brands"""
    query = select(Brand).where(Brand.is_active == True)
    result = await db.execute(query)
    brands = result.scalars().all()
    return brands

@router.post("/", response_model=BrandSchema)
async def create_brand(brand: BrandCreate, db: AsyncSession = Depends(get_db)):
    """Create a new brand"""
    db_brand = Brand(**brand.dict())
    db.add(db_brand)
    await db.commit()
    await db.refresh(db_brand)
    return db_brand