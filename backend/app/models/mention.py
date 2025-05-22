# backend/app/models/mention.py
from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    
    # Content
    platform = Column(String(20), nullable=False)  # twitter, reddit, news
    content = Column(Text, nullable=False)
    url = Column(String(500))
    author = Column(String(100))
    
    # Analysis Results
    sentiment_score = Column(Float)  # -1 to 1
    crisis_probability = Column(Float)  # 0 to 1
    influence_score = Column(Float)  # 0 to 1
    
    # Metadata
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))