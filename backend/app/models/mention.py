from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..core.database import Base

class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    
    # Content fields
    content = Column(Text, nullable=False)
    title = Column(String(500))
    url = Column(String(1000))
    author = Column(String(255))
    platform = Column(String(100), nullable=False)  # twitter, facebook, instagram, etc.
    
    # Timestamps
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Analysis fields
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    sentiment_label = Column(String(20))  # positive, negative, neutral
    emotion_scores = Column(Text)  # JSON string of emotion analysis
    crisis_probability = Column(Float, default=0.0)  # 0 to 1
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    
    # Relationships
    brand = relationship("Brand", back_populates="mentions")