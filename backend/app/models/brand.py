# backend/app/models/brand.py
from sqlalchemy import Column, String, DateTime, Text, JSON, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    industry = Column(String(50))
    keywords = Column(JSON)  # List of keywords to monitor
    sentiment_threshold = Column(Float, default=-0.5)  # Crisis threshold
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Monitoring settings
    monitor_twitter = Column(Boolean, default=True)
    monitor_news = Column(Boolean, default=True)
    monitor_reddit = Column(Boolean, default=False)