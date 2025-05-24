# backend/app/models/mention.py
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  # String instead of UUID
    brand_id = Column(String, ForeignKey("brands.id"))
    content = Column(String)
    platform = Column(String)
    sentiment_score = Column(Float)
    sentiment_label = Column(String)
    crisis_probability = Column(Float)
    published_at = Column(DateTime(timezone=True))
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())