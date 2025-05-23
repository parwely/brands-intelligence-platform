from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class MentionBase(BaseModel):
    content: str
    title: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    platform: str
    published_at: datetime
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    crisis_probability: Optional[float] = 0.0
    likes_count: Optional[int] = 0
    shares_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    reach: Optional[int] = 0

class MentionCreate(MentionBase):
    brand_id: uuid.UUID

class Mention(MentionBase):
    id: uuid.UUID
    brand_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    emotion_scores: Optional[str] = None  # JSON string
    
    class Config:
        from_attributes = True