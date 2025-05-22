# backend/app/api/brands.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from ..core.database import get_db
from ..models.brand import Brand
from ..schemas.brand import Brand as BrandSchema, BrandCreate, BrandUpdate

router = APIRouter()

@router.post("/", response_model=BrandSchema)
async def create_brand(
    brand: BrandCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new brand to monitor"""
    db_brand = Brand(**brand.dict())
    db.add(db_brand)
    await db.commit()
    await db.refresh(db_brand)
    return db_brand

@router.get("/", response_model=List[BrandSchema])
async def list_brands(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all brands"""
    result = await db.execute(
        select(Brand).where(Brand.is_active == True).offset(skip).limit(limit)
    )
    brands = result.scalars().all()
    return brands

@router.get("/{brand_id}", response_model=BrandSchema)
async def get_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get specific brand"""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.put("/{brand_id}", response_model=BrandSchema)
async def update_brand(
    brand_id: uuid.UUID,
    brand_update: BrandUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update brand settings"""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Update fields
    for field, value in brand_update.dict(exclude_unset=True).items():
        setattr(brand, field, value)
    
    await db.commit()
    await db.refresh(brand)
    return brand