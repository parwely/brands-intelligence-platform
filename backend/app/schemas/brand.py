# backend/app/schemas/brand.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class BrandBase(BaseModel):
    name: str
    industry: Optional[str] = None
    keywords: List[str] = []
    sentiment_threshold: float = -0.5

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    keywords: Optional[List[str]] = None
    sentiment_threshold: Optional[float] = None
    is_active: Optional[bool] = None

class Brand(BrandBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True